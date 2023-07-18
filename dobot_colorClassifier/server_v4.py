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

dobot.initialize()

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
MIN_AREA_SIZE = 400 # 小さいマーカーを無視するサイズ
MAX_AREA_SIZE = 1e4

api = None
red_cnt    = 0
blue_cnt   = 0
green_cnt  = 0
yellow_cnt = 0


print('クライアントからの入力待ち状態')
mycam.cam()

# コネクションとアドレスを取得
connection, address = socket1.accept()
print('接続したクライアント情報:'  + str(address))


recvline = ''
sendline = ''
num = 0
dobot.move_home()
i = 0
grip = 0
grip_r = 'g0'
x = 0
first = []
end = []


while True:

    #mycam.cam()
    
    # クライアントからデータを受信
    recvline = connection.recv(4096).decode()
    print('クライアントで入力された文字＝' + str(recvline))

    #データの分割
    if 'g0' in recvline:
        grip_r = 'g0'
        recvline = recvline = recvline.replace('g0','')
        move = 0
        print('開いた状態')

        if recvline == '':
            recvline = '0'

    if 'g1' in recvline:
        grip_r = 'g1'
        recvline = recvline = recvline.replace('g1','')
        move = 0
        print('閉じた状態')

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
        a_x = 100 / (x_1 - x_0 )
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
        if num_x <200:
            num_x =200
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
    
    if grip == 0 and grip_r == 'g1':
        dobot.suctioncup(True, True)
        dType.dSleep(1000)
        grip = 1
        
    if grip == 1 and grip_r == 'g0':
        dobot.suctioncup(True, False)
        grip = 0

    sendline = 'OKです'.encode('utf-8')
    connection.send(sendline)
    #print('クライアントで入力された文字2＝' + str(recvline))
    print('---------------------------------------')
        
# クローズ
connection.close()
socket1.close()
print('サーバー側終了です')