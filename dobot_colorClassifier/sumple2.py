# -*- coding: utf-8 -*-
import tkinter as tk
import tkinter.font as font
import cv2
import PIL.Image, PIL.ImageTk

class App(tk.Tk):
    # 呪文
    def __init__(self, *args, **kwargs):
        # 呪文
        tk.Tk.__init__(self, *args, **kwargs)

        # ウィンドウタイトルを決定
        self.title("Tkinter_cv2")

        # ウィンドウの大きさを決定
        self.geometry("800x600")

        # ウィンドウのグリッドを 1x1 にする
        # この処理をコメントアウトすると配置がズレる
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # MyVideoCaptureクラスをcapとして使う
        self.cap = MyVideoCapture()

#-----------------------------------main_frame---------------------------------
        # メインページフレーム作成
        self.main_frame = tk.Frame()
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        # タイトルラベル作成
        self.titleLabel = tk.Label(self.main_frame, text="Tkinter with cv2", font=('Helvetica', '35'))
        self.titleLabel.pack(anchor='center', expand=True)
        # ボタン生成
        ## カメラ1用フレームに移動
        self.cam1_button = tk.Button(self.main_frame, text="Show Cam1", command=lambda : self.changePage(self.cam1_frame))
        self.cam1_button.pack()
        ## カメラ2用フレームに移動
        self.cam2_button = tk.Button(self.main_frame, text="Show Cam2", command=lambda : self.changePage(self.cam2_frame))
        self.cam2_button.pack()

#-----------------------------------cam1_frame---------------------------------
        # カメラ1用フレーム作成
        self.cam1_frame = tk.Frame()
        self.cam1_frame.grid(row=0, column=0, sticky="nsew")
        # カメラ1用キャンバス作成
        self.cam1_canvas = tk.Canvas(self.cam1_frame, width = self.cap.width, height = self.cap.height)
        self.cam1_canvas.pack()
        # カメラ1用フレームからmainフレームに戻るボタン
        self.back_button = tk.Button(self.cam1_frame, text="Back", command=lambda : self.changePage(self.cam2_frame))
        self.back_button.pack()

#-----------------------------------cam2_frame---------------------------------
        # カメラ2用フレーム作成
        self.cam2_frame = tk.Frame()
        self.cam2_frame.grid(row=0, column=0, sticky="nsew")
        # カメラ2用キャンバス作成
        self.cam2_canvas = tk.Canvas(self.cam2_frame, width = self.cap.width2, height = self.cap.height2)
        self.cam2_canvas.pack()
        # カメラ2用フレームからmainフレームに戻るボタン
        self.back_button = tk.Button(self.cam2_frame, text="Back", command=lambda : self.changePage(self.cam1_frame))
        self.back_button.pack()

        #main_frameを一番上に表示
        self.main_frame.tkraise()

        # 更新作業
        self.update()

    def changePage(self, page):
        '''
        画面遷移用の関数
        '''
        page.tkraise()

    def update(self):
        '''
        各キャンバスへの画像書き込み(opencvのimshow()的な処理)
        '''
        # MyVideoCaptureクラスのget_frameでcam1の映像を取得
        try:
            ret, frame = self.cap.get_frame()
        # 取得できなかったら
        except:
            ret = False
            frame = 0
        # MyVideoCaptureクラスのget_frame2でcam2の映像を取得
        try:
            ret2, frame2 = self.cap.get_frame2()
        except:
            ret2 = False
            frame2 = 0

        if ret:
            self.photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(frame))
            #cam1_canvasに映像表示
            self.cam1_canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)

        if ret2:
            self.photo2 = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(frame2))
            #cam2_canvasに映像表示
            self.cam2_canvas.create_image(0, 0, image=self.photo2, anchor=tk.NW)

        # 100ミリ秒ごとにupdate関数を実行
        self.after(100, self.update)

class MyVideoCapture:
    '''
    cv2での映像取得用クラス
    '''
    def __init__(self):

        # cam1
        self.vid = cv2.VideoCapture(0)
        if not self.vid.isOpened():
            print('camera1 is not Unable')

        # cam2
        self.vid2 = cv2.VideoCapture(1)
        if not self.vid2.isOpened():
            print('camera2 is not Unable')

        #cam1の画面サイズ取得
        self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
        #cam2の画面サイズ取得
        self.width2 = self.vid2.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height2 = self.vid2.get(cv2.CAP_PROP_FRAME_HEIGHT)

    def get_frame(self):
        '''
        cam1画像取得
        '''
        if self.vid.isOpened():
            ret, frame = self.vid.read()
            # 画像が読み込めたらTrueと読み込んだ画像を返す
            if ret:
                return (ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            # 画像が読み込めてなかったらFalseとNoneを返す
            else:
                return (ret, None)
        else:
            return (ret, None)

    def get_frame2(self):
        '''
        cam2画像取得
        '''
        if self.vid2.isOpened():
            ret2, frame2 = self.vid.read()
            # 画像が読み込めたらTrueと読み込んだ画像を返す
            if ret2:
                return (ret2, cv2.cvtColor(frame2, cv2.COLOR_BGR2RGB))
            # 画像が読み込めてなかったらFalseとNoneを返す
            else:
                return (ret2, None)
        else:
            return (ret2, None)

if __name__ == "__main__":
    app = App()
    app.mainloop()