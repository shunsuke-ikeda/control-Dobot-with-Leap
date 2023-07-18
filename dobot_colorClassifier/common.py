'''
Project Name  : dobot_colorClassifier
File Name     : common.py
File Encoding : UTF-8
Copyright © 2020 Afrel Co.,Ltd.
'''

import cv2
import numpy as np

# 0 <= h <= 179 (色相)　OpenCVではmax=179なのでR:0(180)、G:60、B:120となる
# 0 <= s <= 255 (彩度)　黒や白の値が抽出されるときはこの閾値を大きくする
# 0 <= v <= 255 (明度)　これが大きいと明るく、小さいと暗い
RED_LOW_COLOR     = np.array([   0,  75,  75 ])
RED_HIGH_COLOR    = np.array([  20, 255, 255 ])
BLUE_LOW_COLOR    = np.array([ 100,  40,  40 ])
BLUE_HIGH_COLOR   = np.array([ 140, 255, 255 ])
GREEN_LOW_COLOR   = np.array([  40,  40,  40 ])
GREEN_HIGH_COLOR  = np.array([  80, 255, 255 ])
YELLOW_LOW_COLOR  = np.array([  20, 100, 100 ])
YELLOW_HIGH_COLOR = np.array([  40, 255, 255 ])

# フォントの設定
font = cv2.FONT_HERSHEY_DUPLEX
FONT_SIZE  = 0.42
FONT_WIDTH = 1

# 描画用
draw_white  = (200, 200, 200)
draw_black  = ( 50,  50,  50)
draw_red    = ( 50,  50, 200)
draw_blue   = (200,  50,  50)
draw_green  = ( 50, 200,  50)
draw_yellow = ( 50, 200, 200)
