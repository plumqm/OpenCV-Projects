"""
author = qian
date = 2024-10-07

step:
1.opencv 获取视频流
2.在画面上画一个方块
3.通过mediapipe获取手指关键点坐标
4.判断手指是否在方块上
5.若在方块上，方块跟着手指移动

"""

import cv2
import numpy as np

import mediapipe as mp

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

hands = mp_hands.Hands(
    static_image_mode=True,
    max_num_hands=2,
    min_detection_confidence=0.5)

# 1.opencv 获取视频流
cap = cv2.VideoCapture(0)

#获取画面宽和高
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# 方块相关参数
square_x = 100
square_y = 100
square_width = 100
square_color = (255,0,0)
L1 = 0
L2 = 0
on_square = False

while True:

    # 读取每一帧
    ret, frame = cap.read()

    # 处理图像
    frame = cv2.flip(frame, 1)  # 镜像

    # mediapipe处理
    frame.flags.writeable = False
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame)

    frame.flags.writeable = True    
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    # 判断是否出现手
    if results.multi_hand_landmarks:
    
        # 解析遍历每一双手
        for hand_landmarks in results.multi_hand_landmarks:

            # 绘制21个关键点
            mp_drawing.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS,
                mp_drawing_styles.get_default_hand_landmarks_style(),
                mp_drawing_styles.get_default_hand_connections_style())

        # 保存21个x，y坐标
        x_list = [landmark.x for landmark in hand_landmarks.landmark]
        y_list = [landmark.y for landmark in hand_landmarks.landmark]

        # 获取食指指尖
        index_finger_X = int(x_list[8] * width)
        index_finger_Y = int(y_list[8] * height)

        # 获取中指指尖
        middle_finger_X = int(x_list[12] * width)
        middle_finger_Y = int(y_list[12] * height)

        # 计算食指中指指尖距离
        finger_len = np.sqrt((middle_finger_X - index_finger_X)**2 + (middle_finger_Y - index_finger_Y)**2)

        # cv2.circle(frame, (index_finger_X,index_finger_Y)
        # ,20 ,(255,0,255) ,-1)

        # 手指是否在方块上
        if square_x <= x_list[4] <= square_x + square_width and square_y <= y_list[4] <= square_y + square_width:
            square_x += (x_list[4] - square_x) / 10
            square_y += (y_list[4] - square_y) / 10

        # 如果距离小于30算激活
        if finger_len < 30:
            # 判断食指指尖在不在方块上
            if (square_x <= index_finger_X <= square_x + square_width and square_y <= index_finger_Y <= square_y + square_width):
                if on_square == False :
                    L1 = abs(index_finger_X - square_x)
                    L2 = abs(index_finger_Y - square_y)
                    on_square = True
                    square_color = (255,0,255)
            else :
                pass

            if on_square == True:
                square_x = index_finger_X - L1
                square_y = index_finger_Y - L2

        else :
            on_square = False
            square_color = (255,0,0)

    # 2. 在画面上画一个方块
    # cv2.rectangle(frame, (square_x, square_y), (square_x+square_width, square_y+square_width), (255, 0, 0), -1)

    # 画半透明方块
    overlay = frame.copy()
    cv2.rectangle(frame, (square_x, square_y), 
    (square_x+square_width, square_y+square_width), 
    square_color, -1)

    frame = cv2.addWeighted(overlay,0.5,frame,0.5,0)
    # 显示
    cv2.imshow('Virtual drag', frame)

    if cv2.waitKey(10) & 0xFF == 27:
        break 

cap.release()
cv2.destroyAllWindows()


