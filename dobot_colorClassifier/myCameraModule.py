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

# 領域抽出用の最小／最大サイズ
MIN_AREA_SIZE = 400 # 小さいマーカーを無視するサイズ
MAX_AREA_SIZE = 1e4

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

def cam():
     # VideoCaptureのインスタンスを作成する（5-1）
        cap = cv2.VideoCapture(0)

        '''
        print("n - - - - - - - - - - ")
        # camset.camera_set(cv2, cap, gain = **調整した値**, exposure = **調整した値**.)
        camset.camera_get(cv2, cap)
        print(" - - - - - - - - - - n")
        '''

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
    


