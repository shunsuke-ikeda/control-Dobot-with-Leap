# coding: utf-8

# ソケット通信(サーバー側)
import socket
#from typing_extensions import get_origin

#dobot
import DobotDllType as dType
from DobotDllType import PTPMode, JC, DobotConnect


# APIをロードし、DOBOTに接続する
api = dType.load()

# ご使用に応じてCOMポート番号を変更ください
state = dType.ConnectDobot(api, "COM3", 115200)[0]
if not state == DobotConnect.DobotConnect_NoError:
    print("Could not connect to DOBOT")
    exit()

# 初期設定
dType.SetCmdTimeout(api, 3000)
dType.SetQueuedCmdClear(api)
dType.SetQueuedCmdStartExec(api)

deviceName = "DOBOT Magician"
dType.SetDeviceName(api, deviceName)

dType.SetJOGJointParams(api, 50, 50, 50, 50, 50, 50, 50, 50, True)
dType.SetJOGCoordinateParams(api, 50, 50, 50, 50, 50, 50, 50, 50, True)
dType.SetJOGCommonParams(api, 100, 100, True)
dType.SetPTPJointParams(api, 200, 200, 200, 200, 200, 200, 200, 200, True)
dType.SetPTPCoordinateParams(api, 600, 600, 600, 600, True)
dType.SetPTPJumpParams(api, 20, 100, True)
dType.SetPTPCommonParams(api, 30, 30, True)
dType.SetHOMEParams(api, 200, 0, 0, 0, True)
dType.SetEndEffectorParams(api, 59.7 ,0, 0, 0)


host1 = '192.168.1.134'
port1 = 8765

socket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket1.bind((host1, port1))
socket1.listen(1)

print('クライアントからの入力待ち状態')

# コネクションとアドレスを取得
connection, address = socket1.accept()
print('接続したクライアント情報:'  + str(address))

# 無限ループ　byeの入力でループを抜ける
recvline = ''
sendline = ''
num = 0
dType.SetHOMECmdEx(api, 0, True)
i = 0
grip = 0
grip_r = 'g0'

while True:

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
        a_z = 90 / (z_1 - z_0)
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
        if num_z < -40:
            num_z = -40
        if num_z >50:
            num_z = 50

        move = 0
            
        dType.SetPTPCmdEx(api, PTPMode.PTPMOVLXYZMode, num_x, num_y, num_z, 0, True)
        print('x:' + str(num_x))
        print('y:' + str(num_y))
        print('z:' + str(num_z))
        print('x式:x='+ str(a_x) + 'x+' + str(b_x))
        print('y式:y='+ str(a_y) + 'y+' + str(b_y))
        print('z式:z='+ str(a_z) + 'y+' + str(b_z))
    
    if grip == 0 and grip_r == 'g1':
        dType.SetEndEffectorSuctionCupEx(api, True, True, True)
        dType.dSleep(1000)
        grip = 1
        
    if grip == 1 and grip_r == 'g0':
        dType.SetEndEffectorSuctionCupEx(api, True, False, True)
        dType.dSleep(1000)
        grip = 0


    if recvline == 'bye':
        dType.SetQueuedCmdStopExec(api)
        dType.DisconnectDobot(api)
        break
    
    try:

        if i % 2 == 0:
            sendline = 'OKです'.encode('utf-8')

        else:
            sendline = 'NGです'.encode('utf-8')
        connection.send(sendline)

    finally:
        #print('クライアントで入力された文字2＝' + str(recvline))
        print('---------------------------------------')
        
# クローズ
connection.close()
socket1.close()
print('サーバー側終了です')