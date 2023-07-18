'''
Project Name  : dobot_colorClassifier
File Name     : opencv_colorClassifier.py
File Encoding : UTF-8
Copyright © 2020 Afrel Co.,Ltd.
'''

import cv2
import numpy as np
from enum import IntEnum, auto

# DOBOT、WEBカメラ制御用モジュール、変換行列のインポート（1）
import cameraSetting as camset
import myDobotModule as dobot
from TransformationMatrix import MATRIX
MATRIX = np.array(MATRIX)
from common import *

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

    arm_x = 200
    arm_y = 100
    arm_z = 50
    dobot.move(arm_x, arm_y, arm_z, arm_r)
    dobot.wait(0.5)

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

    # アームを元の位置に戻す（2-5）
    arm_x = 200
    arm_y = 100
    dobot.move(arm_x, arm_y, arm_z, arm_r)
    return True


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


# カラーブロックを仕分ける（5）
if __name__ == '__main__':
    # VideoCaptureのインスタンスを作成する（5-1）
    cap = cv2.VideoCapture(0)

    print("\n - - - - - - - - - - ")
    # camset.camera_set(cv2, cap, gain = **調整した値**, exposure = **調整した値**.)
    camset.camera_get(cv2, cap)
    print(" - - - - - - - - - - \n")

    # DOBOTの初期化処理
    dobot.initialize()
    print()
    print(" Press [ H ] key to move Home-Position.")
    print()
    print(" Press [ R ] key to pick up a RED block.")
    print(" Press [ B ] key to pick up a BLUE block.")
    print(" Press [ G ] key to pick up a GREEN block.")
    print(" Press [ Y ] key to pick up a YELLOW block.")
    print()
    print(" Press [ C ] key to Gain, Exposure setting.")
    print(" Press [ESC] key to exit.")
    print()

    while True:
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


        # キー入力を1ms待つ
        k = cv2.waitKey(1)

        # 「ESC（27）」キーを押す
        # プログラムを終了する
        if k == 27:
            break

        # 「C」キーを押す
        # WEBカメラのゲイン値、露出の値を調整する
        elif k == ord('c'):
            g = input("gain     : ")
            e = input("exposure : ")
            print("\n - - - - - - - - - - ")
            camset.camera_set(cv2, cap, gain = float(g), exposure = float(e))
            camset.camera_get(cv2, cap)
            print(" - - - - - - - - - - \n")

        # 「H」キーを押す
        # DOBOTをホームポジションに移動させる（位置リセット）
        elif k == ord('h'):
            dobot.move_home()

        # 「R」キーを押す
        # 取得した座標を使って赤のブロックを拾いに行く
        elif k == ord('r'):
            roop_flg = False
            if pos_red != None:
            	# カラーブロックのカメラ画像をロボット座標系に変換する（5-4）
                move_x, move_y = transform_coordinate(pos_red[0], pos_red[1])
                print("camera position (%d, %d)  -->  dobot position (%d, %d)" % (pos_red[0], pos_red[1], move_x, move_y))
                # カラーブロックを所定の場所へ移動する（5-5）
                move_color(Color.RED, move_x, move_y)
            else:
                print("--- not find RED block ---")

        # 「B」キーを押す
        # 取得した座標を使って青のブロックを拾いに行く
        elif k == ord('b'):
            if pos_blue != None:
                move_x, move_y = transform_coordinate(pos_blue[0], pos_blue[1])
                print("camera position (%d, %d)  -->  dobot position (%d, %d)" % (pos_blue[0], pos_blue[1], move_x, move_y))
                move_color(Color.BLUE, move_x, move_y)
            else:
                print("--- not find BLUE block ---")

        # 「G」キーを押す
        # 取得した座標を使って緑のブロックを拾いに行く
        elif k == ord('g'):
            if pos_green != None:
                move_x, move_y = transform_coordinate(pos_green[0], pos_green[1])
                print("camera position (%d, %d)  -->  dobot position (%d, %d)" % (pos_green[0], pos_green[1], move_x, move_y))
                move_color(Color.GREEN, move_x, move_y)
            else:
                print("--- not find GREEN block ---")

        # 「Y」キーを押す
        # 取得した座標を使って黄のブロックを拾いに行く
        elif k == ord('y'):
            if pos_yellow != None:
                move_x, move_y = transform_coordinate(pos_yellow[0], pos_yellow[1])
                print("camera position (%d, %d)  -->  dobot position (%d, %d)" % (pos_yellow[0], pos_yellow[1], move_x, move_y))
                move_color(Color.YELLOW, move_x, move_y)
            else:
                print("--- not find YELLOW block ---")

    # プログラムの終了処理（5-6）
    # DOBOT終了処理
    dobot.finalize()
    # キャプチャをリリースして、ウィンドウをすべて閉じる
    cap.release()
    cv2.destroyAllWindows()
