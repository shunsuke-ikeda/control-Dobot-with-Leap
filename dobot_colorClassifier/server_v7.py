#画像認識

# coding: utf-8

# ソケット通信(サーバー側)
import socket
#from typing_extensions import get_origin

#dobot
import DobotDllType as dType
from DobotDllType import PTPMode, JC, DobotConnect

#opencv
import cv2
import numpy as np
from enum import IntEnum, auto

# DOBOT、WEBカメラ制御用モジュール、変換行列のインポート（1）
import cameraSetting as camset
import myDobotModule as dobot
from TransformationMatrix import MATRIX
MATRIX = np.array(MATRIX)
from common import *
import myCameraModule as mycam
import myCvModule as mycv

dobot.initialize()

# カラーブロックを移動する（2）
def move_color(color, x, y):
    '''
    指定したX,Y座標にあるブロックを拾い、指定した色に応じた位置に移動する。
    '''
    arm_x = x
    arm_y = y
    arm_z = 0
    arm_r = 0

    # 指定したブロックの上にアームを移動（2-1）
    dobot.move(arm_x, arm_y, arm_z, arm_r)
    dobot.wait(0.5)
    dobot.suctioncup(True, False)

    # ブロックにアームを降ろし、吸引カップで掴む（2-2）
    arm_z = -50
    dobot.move(arm_x, arm_y, arm_z, arm_r)
    dobot.wait(0.5)
    dobot.suctioncup(True, True)
    dobot.wait(0.5)

    # ブロックを持ち上げる（2-3）
    arm_z = 0
    dobot.move(arm_x, arm_y, arm_z, arm_r)
    dobot.wait(0.5)

    '''
    arm_x = 200
    arm_y = 100
    arm_z = 50
    dobot.move(arm_x, arm_y, arm_z, arm_r)
    dobot.wait(0.5)
    '''

    '''
    # ブロックを所定の場所へ降ろす（2-4）
    global red_cnt
    global blue_cnt
    global green_cnt
    global yellow_cnt

    arm_x = 150 + 50 * color
    arm_y = 100
    dobot.move(arm_x, arm_y, arm_z, arm_r)
    dobot.wait(0.5)

    if color == Color.RED:
        arm_z = -40 + (20 * red_cnt)
        red_cnt = red_cnt + 1
    elif color == Color.BLUE:
        arm_z = -40 + (20 * blue_cnt)
        blue_cnt = blue_cnt + 1
    elif color == Color.GREEN:
        arm_z = -40 + (20 * green_cnt)
        green_cnt = green_cnt + 1
    elif color == Color.YELLOW:
        arm_z = -40 + (20 * yellow_cnt)
        yellow_cnt = yellow_cnt + 1

    dobot.move(arm_x, arm_y, arm_z, arm_r)
    dobot.wait(0.5)
    dobot.suctioncup(True, False)
    dobot.wait(0.5)

    arm_z = 50
    dobot.move(arm_x, arm_y, arm_z, arm_r)
    dobot.wait(0.5)

    dobot.suctioncup(False, False)
    '''

    '''
    # アームを元の位置に戻す（2-5）
    arm_x = 200
    arm_y = 100
    dobot.move(arm_x, arm_y, arm_z, arm_r)
    return True
    '''

# 指定した色の領域の中心点を取得する（4）
def find_specific_color(color_name, frame, edframe, low, high):
    '''
    指定された色空間の範囲から色を抽出し、輪郭から領域、矩形を取得する
    '''
    # HSV色空間に変換
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    # 色を抽出する
    ex_img = cv2.inRange(hsv, low, high)
    # 1/4サイズに縮小して表示
    ex_img_s = cv2.resize(ex_img, (int(ex_img.shape[1]/2), int(ex_img.shape[0]/2)))
    cv2.imshow(color_name, ex_img_s)

    # 輪郭抽出
    contours, hierarchy = cv2.findContours(ex_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    mp_x = mp_y = None
    for i, contour in enumerate(contours):
        # 輪郭の領域を計算
        area = cv2.contourArea(contour)
        # ノイズ（小さすぎる領域）と全体の輪郭（大きすぎる領域）を除外
        if area < MIN_AREA_SIZE or MAX_AREA_SIZE < area:
            continue

        # 輪郭に外接する長方形を取得する。
        x, y, width, height = cv2.boundingRect(contour)
        # 長方形を描画する。
        cv2.rectangle(edframe, (x, y), (x+width, y+height), draw_red, thickness=1)

        # 輪郭データを浮動小数点型の配列に格納
        X = np.array(contour, dtype=np.float).reshape((contour.shape[0], contour.shape[2]))
        # PCA（１次元）
        mean, eigenvectors = cv2.PCACompute(X, mean=np.array([], dtype=np.float), maxComponents=1)

        # 中心を描画
        mp_x = int(mean[0][0])
        mp_y = int(mean[0][1])
        cv2.drawMarker(edframe, (mp_x, mp_y), draw_red, cv2.MARKER_TILTED_CROSS, thickness = 1)

        # 情報を描画
        label = " Mid : (" + str(mp_x) + ", " + str(mp_y) + ")"
        cv2.putText(edframe, label, (x+width, y+10), font, FONT_SIZE, draw_green, FONT_WIDTH, cv2.LINE_AA)
        label = " Area: " + str(area)
        cv2.putText(edframe, label, (x+width, y+30), font, FONT_SIZE, draw_green, FONT_WIDTH, cv2.LINE_AA)

    if mp_x == None and mp_y == None: return None
    return (mp_x, mp_y)

    # カメラ座標系をロボット座標系へ変換する（3）
def transform_coordinate(pos_x, pos_y):
    '''
    入力した座標（カメラ座標系）を変換行列を使用して、DOBOT制御用の座標（ロボット座標系）に変換する
    '''
    global MATRIX
    pos = np.array([ [pos_x, pos_y] ], dtype='float32')
    pos = np.array([pos])
    transform_pos = cv2.perspectiveTransform(pos, MATRIX)
    return int(transform_pos[0][0][0]), int(transform_pos[0][0][1])

host1 = '192.168.1.134'
port1 = 8765

socket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket1.bind((host1, port1))
socket1.listen(1)

class Color(IntEnum):
    RED    = 0
    BLUE   = auto()
    GREEN  = auto()
    YELLOW = auto()

# 領域抽出用の最小／最大サイズ
MIN_AREA_SIZE = 800 # 小さいマーカーを無視するサイズ
MAX_AREA_SIZE = 1e4

api = None
red_cnt    = 0
blue_cnt   = 0
green_cnt  = 0
yellow_cnt = 0


print('クライアントからの入力待ち状態')


# コネクションとアドレスを取得
connection, address = socket1.accept()
print('接続したクライアント情報:'  + str(address))


recvline = ''
sendline = ''
color_move = 0
num = 0
dobot.move_home()
i = 0
grip = 0
grip_r = 'g0'
color =0 
color_g = 0
x = 0
first = []
end = []


while True:

    #mycam.cam()
    print('color_move:' + str(color_move))
    print('color_g:' + str(color_g))
    print('color:' + str(color))
    print('grip:' + str(grip))
    # クライアントからデータを受信
    recvline = connection.recv(4096).decode()
    print('クライアントで入力された文字＝' + str(recvline))

    #データの分割
    if 'g0' in recvline:
        if color_move == 1:
            color_g = 2
            color_move = 2
            recvline = recvline.replace('g0','')
            print('g1')
        elif color_move == 2 and color_g == 1:
            color = 1
            recvline = recvline.replace('g0','')
            print('1')
        elif grip == 2:
            grip = 0
        else:
            grip_r = 'g0'
            recvline = recvline.replace('g0','')
            move = 0
            print('開いた状態')
        if recvline == '':
            recvline = '0'


    if 'g1' in recvline:
        if color_move == 1:
            color_g = 1
            color_move = 2
            recvline = recvline.replace('g1','')
            print('g2')
        elif color_move == 2 and color_g == 2:
            color = 3
            recvline = recvline.replace('g1','')
            print('3')
        elif grip == 2:
            grip =1
            recvline = recvline.replace('g1','')
            print('グリップ')
        elif recvline == '':
            recvline = '0'
        else:
            grip_r = 'g1'
            recvline = recvline.replace('g1','')
            move = 0
            print('閉じた状態')
        if recvline == '':
            recvline = '0'

        if recvline == '':
            recvline = '0'

    if 'g2' in recvline:
        if color_move == 2 and color_g == 1:
            color = 2
            recvline = recvline.replace('g2','')
            print('2')
        elif color_move == 2 and color_g == 2:
            color = 4
            recvline = recvline.replace('g2','')
            print('4')
        elif grip == 2:
            recvline = recvline.replace('g2','')
            print('そのまま')
        else:
            grip_r = 'g2'
            recvline = recvline.replace('g2','')
            move = 0
            color_move = 1
            print('カメラ起動')

        if recvline == '':
            recvline = '0'


    if recvline[0] == '(':
        x = recvline.rfind('(')
        recvline = recvline[x:]
        recvline = recvline.replace('(','')
        recvline = recvline.replace(')','')
        recvline_y = recvline.split(', ',2)[0]
        recvline_z = recvline.split(', ',2)[1]
        recvline_x = recvline.split(', ',2)[2]
        move = 1

    #gはグリップ状態の判定
    if move == 1 and i == 1:
        print('---右上---')
        i = 2
        print(recvline_y)
        print(recvline_x)
        print(recvline_z)
        y_1 = float(recvline_y)
        x_1 = float(recvline_x)
        z_1 = float(recvline_z)

        #xとyとｚの傾き
        a_y = (-200) / (y_1 - y_0 )
        a_x = 180 / (x_1 - x_0 )
        a_z = 100 / (z_1 - z_0)
        print(a_y)
        print(a_x)

        #xとyとｚの切片
        b_y = 100 - (a_y * y_0)
        b_x = 300 - (a_x * x_1)
        b_z = 50 - (a_z * z_1)
        print(b_y)
        print(b_x)      


    if i == 0:
        print('---左下---')
        print(recvline_y)
        print(recvline_x)
        print(recvline_z)
        y_0 = float(recvline_y)
        x_0 = float(recvline_x)
        z_0 = float(recvline_z)
        i = 1
    if color_move == 0:
        if move == 1 and i == 2:
            num_y = float(recvline_y)
            num_x = float(recvline_x)
            num_z = float(recvline_z)
            num_y = a_y * num_y + b_y
            num_x = a_x * num_x + b_x
            num_z = a_z * num_z + b_z
            if num_y > 100:
                num_y = 100
            if num_y < -100:
                num_y = -100
            if num_x > 300:
                num_x = 300
            if num_x <120:
                num_x =120
            if num_z < -50:
                num_z = -50
            if num_z >50:
                num_z = 50
            move = 0
                
            dobot.move(num_x, num_y, num_z, 0)
            print('x:' + str(num_x))
            print('y:' + str(num_y))
            print('z:' + str(num_z))
            print('x式:x='+ str(a_x) + 'x+' + str(b_x))
            print('y式:y='+ str(a_y) + 'y+' + str(b_y))
            print('z式:z='+ str(a_z) + 'y+' + str(b_z))

            #mycam.cam()
            
            sendline = 'OK Boy'.encode('utf-8')
            connection.send(sendline)

    if color_move == 0:
        if grip == 1 and grip_r == 'g0':
            dobot.suctioncup(True, False)
            grip = 0

        if grip == 0 and grip_r == 'g1':
            dobot.suctioncup(True, True)
            dType.dSleep(1000)
            grip = 1

        if grip_r == 'g2':
            color_move = 1
            color = 0


    
    if color_move == 2 and color != 0:
        # VideoCaptureのインスタンスを作成する（5-1）
        cap = cv2.VideoCapture(0)
        camset.camera_get(cv2, cap)
         # VideoCaptureから1フレーム読み込む（5-2）
        ret, frame = cap.read()
        ret, edframe = cap.read()
        # 加工なし画像を表示する
        cv2.imshow('Raw Frame', frame)

        # カラーブロック座標（カメラ座標系）を取得する（5-3）
        # RED
        pos_red = find_specific_color("RED", frame, edframe, RED_LOW_COLOR, RED_HIGH_COLOR)
        # BLUE
        pos_blue = find_specific_color("BLUE", frame, edframe, BLUE_LOW_COLOR, BLUE_HIGH_COLOR)
        # YELLOW
        pos_yellow = find_specific_color("YELLOW", frame, edframe, YELLOW_LOW_COLOR, YELLOW_HIGH_COLOR)
        # GREEN
        pos_green = find_specific_color("GREEN", frame, edframe, GREEN_LOW_COLOR, GREEN_HIGH_COLOR)

        # 加工済の画像を表示する
        cv2.imshow('Edited Frame', edframe)
        roop_flg = False

        if color == 1:
            if pos_red != None:
                # カラーブロックのカメラ画像をロボット座標系に変換する（5-4）
                move_x, move_y = transform_coordinate(pos_red[0], pos_red[1])
                print("camera position (%d, %d)  -->  dobot position (%d, %d)" % (pos_red[0], pos_red[1], move_x, move_y))
                # カラーブロックを所定の場所へ移動する（5-5）
                move_color(Color.RED, move_x, move_y)
                grip = 2
            else:
                print("--- not find RED block ---")
        
        elif color == 2:
            # 取得した座標を使って黄のブロックを拾いに行く
            if pos_yellow != None:
                move_x, move_y = transform_coordinate(pos_yellow[0], pos_yellow[1])
                print("camera position (%d, %d)  -->  dobot position (%d, %d)" % (pos_yellow[0], pos_yellow[1], move_x, move_y))
                move_color(Color.YELLOW, move_x, move_y)
                grip = 2
            else:
                print("--- not find YELLOW block ---")

        elif color == 3:
            if pos_blue != None:
                move_x, move_y = transform_coordinate(pos_blue[0], pos_blue[1])
                print("camera position (%d, %d)  -->  dobot position (%d, %d)" % (pos_blue[0], pos_blue[1], move_x, move_y))
                move_color(Color.BLUE, move_x, move_y)
                grip = 1
            else:
                print("--- not find BLUE block ---")
        elif color == 4:    
            if pos_green != None:
                move_x, move_y = transform_coordinate(pos_green[0], pos_green[1])
                print("camera position (%d, %d)  -->  dobot position (%d, %d)" % (pos_green[0], pos_green[1], move_x, move_y))
                move_color(Color.GREEN, move_x, move_y)
                grip = 2
            else:
                print("--- not find GREEN block ---")
        
        color_move =0
        color_g = 0
        color = 0
        grip_r = ''
        

    sendline = 'OKです'.encode('utf-8')
    connection.send(sendline)
    #print('クライアントで入力された文字2＝' + str(recvline))
    print('---------------------------------------')
        
# クローズ
connection.close()
socket1.close()
print('サーバー側終了です')