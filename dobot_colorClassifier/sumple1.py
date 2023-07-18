# coding:utf-8
import socket
import numpy as np
import cv2
import time
import configparser

config = configparser.ConfigParser()
config.read('./connection.ini', 'UTF-8')

# 全体の設定
FPS = 12
INDENT = '    '

# カメラ設定
CAMERA_ID = 0
CAMERA_ID0 = 0
CAMERA_ID1 = 1
CAMERA_FPS = 12
CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720

# サーバ設定
SERVER_IP = '10.228.17.157'
SERVER_PORT = int(config.get('server', 'port'))

# パケット設定
HEADER_SIZE = int(config.get('packet', 'header_size'))

# 画像設定
IMAGE_WIDTH = int(config.get('packet', 'image_width'))
IMAGE_HEIGHT = int(config.get('packet', 'image_height'))
IMAGE_QUALITY = 30

# カメラ設定適用
cam0 = cv2.VideoCapture(CAMERA_ID0)
cam0.set(cv2.CAP_PROP_FPS, CAMERA_FPS)
cam0.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
cam0.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)

cam1 = cv2.VideoCapture(CAMERA_ID1)
cam1.set(cv2.CAP_PROP_FPS, CAMERA_FPS)
cam1.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
cam1.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)

# カメラ情報表示
print('Camera {')
print(INDENT + 'ID    : {},'.format(CAMERA_ID0))
print(INDENT + 'FPS   : {},'.format(cam0.get(cv2.CAP_PROP_FPS)))
print(INDENT + 'WIDTH : {},'.format(cam0.get(cv2.CAP_PROP_FRAME_WIDTH)))
print(INDENT + 'HEIGHT: {}'.format(cam0.get(cv2.CAP_PROP_FRAME_HEIGHT)))
print('}')

print('Camera {')
print(INDENT + 'ID    : {},'.format(CAMERA_ID1))
print(INDENT + 'FPS   : {},'.format(cam0.get(cv2.CAP_PROP_FPS)))
print(INDENT + 'WIDTH : {},'.format(cam0.get(cv2.CAP_PROP_FRAME_WIDTH)))
print(INDENT + 'HEIGHT: {}'.format(cam0.get(cv2.CAP_PROP_FRAME_HEIGHT)))
print('}')

# クライアントに接続
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((SERVER_IP, SERVER_PORT))
s.listen(1)
soc, addr = s.accept()

print('Server {')
print(INDENT + 'IP   : {},'.format(SERVER_IP))
print(INDENT + 'PORT : {}'.format(SERVER_PORT))
print('}')

# クライアント情報表示
print('Client {')
print(INDENT + 'IP   : {},'.format(addr[0]))
print(INDENT + 'PORT : {}'.format(addr[1]))
print('}')

# メインループ
while True:
    loop_start_time = time.time()
    #recvid = soc.recv(4096).decode()


    # 送信用画像データ作成
    flag, img0 = cam0.read()
    resized_img0 = cv2.resize(img0, (IMAGE_WIDTH, IMAGE_HEIGHT))
    (status, encoded_img0) = cv2.imencode('.jpg', resized_img0, [int(cv2.IMWRITE_JPEG_QUALITY), IMAGE_QUALITY])

    flag, img1 = cam1.read()
    resized_img1 = cv2.resize(img1, (IMAGE_WIDTH, IMAGE_HEIGHT))
    (status, encoded_img1) = cv2.imencode('.jpg', resized_img1, [int(cv2.IMWRITE_JPEG_QUALITY), IMAGE_QUALITY])

    # パケット構築
    packet_body0 = encoded_img0.tostring()
    packet_header0 = len(packet_body0).to_bytes(HEADER_SIZE, 'big') 
    packet0 = packet_header0 + packet_body0

    packet_body1 = encoded_img1.tostring()
    packet_header1 = len(packet_body1).to_bytes(HEADER_SIZE, 'big') 
    packet1 = packet_header1 + packet_body1

    # パケット送信
    try:    
        #CAMERA_ID = int(recvid)
        #if CAMERA_ID == 0:
        soc.sendall(packet0)
        #elif CAMERA_ID == 1:
        soc.sendall(packet1)
    except socket.error as e:
        print('Connection closed.')
        break

    # FPS制御
    time.sleep(max(0, 1 / FPS - (time.time() - loop_start_time)))

s.close()