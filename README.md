# control-Dobot-with-Leap
as a basic research, we use a small motion controller, Leap Motion, to detect the angle of a finger, and a robot arm, Dobot Magician, to create a tele-operation system.
基礎研究として，小型モーションコントローラLeap Motionを用いて指の角度検出を行い，ロボットアームとしてDobot Magcianを用いて，遠隔操作システムの創出を行う．

dobot-colorclassifierはDobot Magicianの制御、L_D_v4.cs,zikken.csはLeap Motionの制御に用いる。

提案手法2.jpgのようにLeap MotionをつないだPCとDobot MagicianをつないだPCをソケット通信を用いて遠隔操作を可能にする。Dobot MagicianをつないだPCには画像認識用のカメラを繋げることで画像認識による把持操作支援方式が可能になる。

dobot-colarclassifierに関して、opencv-setting.pyにより画像認識用のカメラの設定が行われる。server_v7.pyにより画像認識を用いたDobot Magicianの遠隔操作が行われる。
