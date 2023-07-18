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

    arm_x = 200
    arm_y = 100
    arm_z = 50
    dobot.move(arm_x, arm_y, arm_z, arm_r)
    dobot.wait(0.5)

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
