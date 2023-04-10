import socket
import cv2
import numpy as np
from tools.custom import LandDetect
import time
from pathlib import Path
import os

root = Path(__file__).parent.absolute()

global sendBack_angle, sendBack_Speed, current_speed, current_angle
sendBack_angle = 0
sendBack_Speed = 0
current_speed = 0
current_angle = 0

output_size = (640, 360)
# Create a socket object
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Define the port on which you want to connect
PORT = 54321
# connect to the server on local computer
s.connect(('127.0.0.1', PORT))


def Control(angle, speed):
    global sendBack_angle, sendBack_Speed
    sendBack_angle = angle
    sendBack_Speed = speed


if __name__ == "__main__":

    land_detector = LandDetect('pidnet-s', os.path.join(root,'output/mydata/pidnet_small_camvid/best.pt'))

    try:
        cnt_fps = 0
        t_pre = 0
        while True:
            """
            - Chương trình đưa cho bạn 1 giá trị đầu vào:
                * image: hình ảnh trả về từ xe
                * current_speed: vận tốc hiện tại của xe
                * current_angle: góc bẻ lái hiện tại của xe
            - Bạn phải dựa vào giá trị đầu vào này để tính toán và
            gán lại góc lái và tốc độ xe vào 2 biến:
                * Biến điều khiển: sendBack_angle, sendBack_Speed
                Trong đó:
                    + sendBack_angle (góc điều khiển): [-25, 25]
                        NOTE: ( âm là góc trái, dương là góc phải)
                    + sendBack_Speed (tốc độ điều khiển): [-150, 150]
                        NOTE: (âm là lùi, dương là tiến)
            """

            message_getState = bytes("0", "utf-8")
            s.sendall(message_getState)
            state_date = s.recv(100)

            try:
                current_speed, current_angle = state_date.decode(
                    "utf-8"
                    ).split(' ')
            except Exception as er:
                print(er)
                pass

            message = bytes(f"1 {sendBack_angle} {sendBack_Speed}", "utf-8")
            s.sendall(message)
            data = s.recv(100000)

            try:
                image = cv2.imdecode(
                    np.frombuffer(
                        data,
                        np.uint8
                        ), -1
                    )

                # print(current_speed, current_angle)
                # print(image.shape)
                # your process here
                rs_image = land_detector.reference(image, output_size)
                cv2.imshow("IMG_goc", image)
                cv2.imshow("IMG", rs_image)
                cv2.waitKey(1)

                # Control(angle, speed)
                Control(25, 100)
            
                if cnt_fps >= 30:
                    t_cur = time.time()
                    fps = (cnt_fps + 1)/(t_cur - t_pre)
                    t_pre = t_cur
                    print('fps: {:.2f}\r\n'.format(fps))
                    cnt_fps = 0
                
                cnt_fps += 1

            except Exception as er:
                print(er)
                pass

    finally:
        print('closing socket')
        s.close()