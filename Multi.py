import transformations as tf
import pyrealsense2 as rs
import time
import numpy as np
import asyncio
from multiprocessing import Process, Pipe

class Realsense():
    def __init__(self, freq=.02):
        self.pos = None
        self.freq = freq
        self.H_aeroRef_T265Ref = np.array([[0, 0, -1, 0], [1, 0, 0, 0], [0, -1, 0, 0], [0, 0, 0, 1]])
        self.H_T265body_aeroBody = np.linalg.inv(self.H_aeroRef_T265Ref)

        # Declare RealSense pipeline, encapsulating the actual device and sensors
        self.pipe = rs.pipeline()

        # Build config object and request pose data
        self.cfg = rs.config()
        self.cfg.enable_stream(rs.stream.pose)

    def start(self):
        # Start streaming with requested config
        print("Opening Realsense Pipe")
        self.pipe.start(self.cfg)

    def stop(self):
        print("Closing Realsense Pipe")
        self.pipe.stop()
        print("Closed Successful")

    def send_pose(self):
        print(self.pos)

    def update(self):
        # Wait for the next set of frames from the camera
        frames = self.pipe.wait_for_frames()
        # Fetch pose frame
        pose = frames.get_pose_frame()
        if pose:
            # Print some of the pose data to the terminal
            data = pose.get_pose_data()
            H_T265Ref_T265body = tf.quaternion_matrix([data.rotation.w, data.rotation.x, data.rotation.y,
                                                       data.rotation.z])  # in transformations, Quaternions w+ix+jy+kz are represented as [w, x, y, z]!

            # transform to aeronautic coordinates (body AND reference frame!)
            H_aeroRef_aeroBody = self.H_aeroRef_T265Ref.dot(H_T265Ref_T265body.dot(self.H_T265body_aeroBody))

            rpy_rad = np.array(tf.euler_from_matrix(H_aeroRef_aeroBody,
                                                    'sxyz'))  # Rz(yaw)*Ry(pitch)*Rx(roll) body w.r.t. reference frame
            cor = [data.translation.z, data.translation.x, data.translation.z, rpy_rad[2], rpy_rad[1], rpy_rad[0]]
        else:
            cor = [None, None, None, None, None, None]

        y, x, z, ry, rx, rz = cor

        scaled_x = x * 100
        scaled_y = y * 100
        self.pos = (scaled_x, scaled_y, ry)
        # print("Robot Pose: ", self.pos)
        # await self.sio.emit('pose', {'pose' : self.pos})
        # await asyncio.sleep(.2)

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, type, value, traceback):
        self.stop()


def read_tracker(comm):
    time_start = time.time()
    with Realsense() as tracker:
        while time.time() - time_start < 5:
            tracker.update()
            #print(tracker.pos)
            comm.send(tracker.pos)
            time.sleep(tracker.freq)
    print("Done with Realsense")


async def print_data(comm):
    time_start = time.time()
    while time.time() - time_start < 8:
        data = []
        while comm.poll():
            data.append(comm.recv())
        if len(data) > 0:
            print(data[-1])
        await asyncio.sleep(1)
    print("Done Printing Data")

async def print_hello():
    time_start = time.time()
    while time.time() - time_start < 10:
        print("HELLO WORLD!!")
        await asyncio.sleep(1)
    print("Done Printing Hello")

async def main():
    to_tracker, to_host = Pipe(duplex=False)
    p1 = Process(target=read_tracker, args=(to_host,))
    # p2 = Process(target=print_data, args=(to_tracker,))
    print("Starting tasks")
    p1.start()
    print("Tasks p1")
    asyncio.create_task(print_data(to_tracker))
    print("Tasks 1")
    asyncio.create_task(print_hello())
    print("Task 2")
    await asyncio.sleep(20)

    # while p1.is_alive():
    #     data = []
    #     while to_tracker.poll():
    #         data.append(to_tracker.recv())
    #     if len(data) > 0:
    #         print(data[-1])

    # p2.start()
    p1.join()
    await asyncio.gather()
    print("Done")


if __name__ == "__main__":
    asyncio.run(main())
