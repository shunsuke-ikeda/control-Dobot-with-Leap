using UnityEngine;
using System.Collections;
using Leap;
using Leap.Unity;
using System.Collections.Generic;
using UnityEngine.UI;

//socket追加
using System;
using System.Net.Sockets;
using System.Text;
using UnityEngine;

//grip追加
using System.Linq;


public class L_D_v4 : MonoBehaviour
{
    [SerializeField]
    GameObject m_ProviderObject;

    LeapServiceProvider m_Provider;

    public Text scoreText; // 取得した手のトラッキングデータをUIに表示

    public GameObject Apple;

    //grip追加
    private Controller controller;
    private Finger[] fingers;
    private bool[] isGripFingers;
    public enum RSP
    {
        Rock, Scissors, Paper
    }
    public RSP rsp;

    void Start()
    {
        m_Provider = m_ProviderObject.GetComponent<LeapServiceProvider>();
        
        //grip追加
        controller = new Controller();
        fingers = new Finger[5];
        isGripFingers = new bool[5];
    }

    void Update()
    {
        Frame frame = m_Provider.CurrentFrame;

        //grip追加
        //Frame frame = controller.Frame();
        if(frame.Hands.Count != 0)
        {
            //グリップしているかの判定
            List<Hand> hand = frame.Hands;
            fingers = hand[0].Fingers.ToArray();
            isGripFingers = Array.ConvertAll(fingers, new Converter<Finger, bool>(i => i.IsExtended));
            //Debug.Log(isGripFingers[0]+","+ isGripFingers[1] + "," + isGripFingers[2] + "," + isGripFingers[3] + "," + isGripFingers[4]);
            int extendedFingerCount = isGripFingers.Count(n => n == true);
            if(extendedFingerCount == 0)
            {
                rsp = RSP.Rock;
            }
            else if(extendedFingerCount < 4)
            {
                rsp = RSP.Scissors;

            }
            else
            {
                rsp = RSP.Paper;

            }

        }

        // 右手と左手を取得する
        Hand rightHand = null;
        Hand leftHand = null;
        foreach (Hand hand in frame.Hands)
        {
            if (hand.IsRight)
            {
                rightHand = hand;
            }
            if (hand.IsLeft)
            {
                leftHand = hand;
            }
        }

        if (rightHand == null && leftHand == null)
        {
            return;
        }

        Vector3 right_normal;
        Vector3 right_direction;
        Vector3 right_position;
        Vector3 left_normal;
        Vector3 left_direction;
        Vector3 left_position;
        float distance;

        if (rightHand != null && leftHand != null)
        {
            right_normal = rightHand.PalmNormal.ToVector3();
            right_direction = rightHand.Direction.ToVector3();
            right_position = rightHand.PalmPosition.ToVector3();
            left_normal = leftHand.PalmNormal.ToVector3();
            left_direction = leftHand.Direction.ToVector3();
            left_position = leftHand.PalmPosition.ToVector3();
            distance = Vector3.Distance(right_position, left_position);
            scoreText.text = "右手の法線ベクトル: " + right_normal + "\n" +
                             "右手の方向ベクトル: " + right_direction + "\n" +
                             "右手の位置ベクトル: " + right_position + "\n" +
                             "左手の法線ベクトル: " + left_normal + "\n" +
                             "左手の方向ベクトル: " + left_direction + "\n" +
                             "左手の位置ベクトル: " + left_position + "\n" +
                             "内積: " + Vector3.Dot(right_normal, left_normal) + "\n" +
                             "中点: " + Vector3.Lerp(right_position, left_position, 0.5f) + "\n" +
                             "２点間の距離: " + distance;
        }

        if (rightHand != null && leftHand == null)
        {
            right_normal = rightHand.PalmNormal.ToVector3();
            right_direction = rightHand.Direction.ToVector3();
            right_position = rightHand.PalmPosition.ToVector3();
            scoreText.text = "右手の法線ベクトル: " + right_normal + "\n" +
                             "右手の方向ベクトル: " + right_direction + "\n" +
                             "右手の位置ベクトル: " + right_position;
        }
        if (rightHand == null && leftHand != null)
        {
            left_normal = leftHand.PalmNormal.ToVector3();
            left_direction = leftHand.Direction.ToVector3();
            left_position = leftHand.PalmPosition.ToVector3();
            scoreText.text = "左手の法線ベクトル: " + left_normal + "\n" +
                             "左手の方向ベクトル: " + left_direction + "\n" +
                             "左手の位置ベクトル: " + left_position;
        }
    }

    //================================================================================
    // 変数
    //================================================================================
    // この IP アドレスとポート番号はサーバ側と統一すること
    public string m_ipAddress = "192.168.1.153";
    public int    m_port      = 8765;

    private TcpClient     m_tcpClient;
    private NetworkStream m_networkStream;
    private bool          m_isConnection;

    private string m_message_r = "200,250"; // サーバに送信する文字列
    private string m_message_l = "200,250"; // サーバに送信する文字列

    //gripの状況
    //g0は開いている状態
    //g1は握っている状態
    private string g_message_l = "g0";
    int count = 0;
    int grip =0;

    private void Awake()
    {
        try
        {
            // 指定された IP アドレスとポートでサーバに接続します
            m_tcpClient     = new TcpClient( m_ipAddress, m_port );
            m_networkStream = m_tcpClient.GetStream();
            m_isConnection  = true;

            Debug.LogFormat( "接続成功" );
        }
        catch ( SocketException )
        {
            // サーバが起動しておらず接続に失敗した場合はここに来ます
            Debug.LogError( "接続失敗" );
        }
    }

    /// <summary>
    /// GUI を描画する時に呼び出されます
    /// </summary>
    public void OnGUI()
    {
        Frame frame = m_Provider.CurrentFrame;

        // 右手と左手を取得する
        Hand rightHand = null;
        Hand leftHand = null;
        foreach (Hand hand in frame.Hands)
        {
            if (hand.IsRight)
            {
                rightHand = hand;
            }
            if (hand.IsLeft)
            {
                leftHand = hand;
            }
        }

        if (rightHand == null && leftHand == null)
        {
            return;
        }

        Vector3 right_normal;
        Vector3 right_direction;
        Vector3 right_position;
        Vector3 left_normal;
        Vector3 left_direction;
        Vector3 left_position;
        float distance;

        if (rightHand != null && leftHand != null)
        {
            right_normal = rightHand.PalmNormal.ToVector3();
            right_direction = rightHand.Direction.ToVector3();
            right_position = rightHand.PalmPosition.ToVector3();
            left_normal = leftHand.PalmNormal.ToVector3();
            left_direction = leftHand.Direction.ToVector3();
            left_position = leftHand.PalmPosition.ToVector3();
            distance = Vector3.Distance(right_position, left_position);
            m_message_l = Convert.ToString(left_position);
            m_message_r = Convert.ToString(right_position);
        }

        if (rightHand != null && leftHand == null)
        {
            right_normal = rightHand.PalmNormal.ToVector3();
            right_direction = rightHand.Direction.ToVector3();
            right_position = rightHand.PalmPosition.ToVector3();
            m_message_r = Convert.ToString(right_position);
        }

        if (rightHand == null && leftHand != null)
        {
            left_normal = leftHand.PalmNormal.ToVector3();
            left_direction = leftHand.Direction.ToVector3();
            left_position = leftHand.PalmPosition.ToVector3();
            m_message_l = Convert.ToString(left_position);
        }

        // Awake 関数で接続に失敗した場合はその旨を表示します
        if ( !m_isConnection )
        {
            GUILayout.Label( "接続していません" );
            return;
        }

        if ( count == 2)
        {
            System.Threading.Thread.Sleep(100);
            if (rightHand == null && leftHand != null)
            {
                // サーバに文字列を送信します
                var buffer = Encoding.UTF8.GetBytes( m_message_l );
                m_networkStream.Write( buffer, 0, buffer.Length );
                Debug.LogFormat( "送信成功L：{0}", m_message_l );

                if(rsp == RSP.Rock && grip !=1)
                {
                    g_message_l = "g1";
                    buffer = Encoding.UTF8.GetBytes( g_message_l );
                    m_networkStream.Write( buffer, 0, buffer.Length );
                    Debug.LogFormat( "送信成功グリップ：{0}", g_message_l );
                    grip = 1;
                }

                if(rsp == RSP.Paper && grip != 0)
                {
                    g_message_l = "g0";
                    buffer = Encoding.UTF8.GetBytes( g_message_l );
                    m_networkStream.Write( buffer, 0, buffer.Length );
                    Debug.LogFormat( "送信成功グリップ：{0}", g_message_l );
                    grip = 0;
                }

                if(rsp == RSP.Scissors && grip != 2)
                {
                    g_message_l = "g2";
                    buffer = Encoding.UTF8.GetBytes( g_message_l );
                    m_networkStream.Write( buffer, 0, buffer.Length );
                    Debug.LogFormat( "送信成功グリップ：{0}", g_message_l );
                    grip = 2;
                }

            }
            if (rightHand != null && leftHand == null)
            {
                // サーバに文字列を送信します
                var buffer = Encoding.UTF8.GetBytes( m_message_r );
                m_networkStream.Write( buffer, 0, buffer.Length );
                Debug.LogFormat( "送信成功R：{0}", m_message_r );
            }
            if (rightHand != null && leftHand != null)
            {
                var buffer = Encoding.UTF8.GetBytes( m_message_r );
                m_networkStream.Write( buffer, 0, buffer.Length );
                Debug.LogFormat( "送信成功R：{0}", m_message_r );

                buffer = Encoding.UTF8.GetBytes( m_message_l );
                m_networkStream.Write( buffer, 0, buffer.Length );
                Debug.LogFormat( "送信成功L：{0}", m_message_l );
            }
            
        }
        
        // サーバに送信する文字列
        //m_message = GUILayout.TextField( m_message );
        // 送信ボタンが押されたら
        else if ( GUILayout.Button( "送信" ) )
        {
            try
            {
                if (rightHand == null && leftHand != null)
                {
                    // サーバに文字列を送信します
                    var buffer = Encoding.UTF8.GetBytes( m_message_l );
                    m_networkStream.Write( buffer, 0, buffer.Length );
                    Debug.LogFormat( "送信成功L：{0}", m_message_l );

                    if(rsp == RSP.Rock)
                    {
                        g_message_l = "g1";
                        buffer = Encoding.UTF8.GetBytes( g_message_l );
                        m_networkStream.Write( buffer, 0, buffer.Length );
                        Debug.LogFormat( "送信成功グリップ：{0}", g_message_l );
                    }

                    if(rsp == RSP.Paper)
                    {
                        g_message_l = "g0";
                        buffer = Encoding.UTF8.GetBytes( g_message_l );
                        m_networkStream.Write( buffer, 0, buffer.Length );
                        Debug.LogFormat( "送信成功グリップ：{0}", g_message_l );
                    }

                    if(rsp == RSP.Scissors )
                    {
                        g_message_l = "g2";
                        buffer = Encoding.UTF8.GetBytes( g_message_l );
                        m_networkStream.Write( buffer, 0, buffer.Length );
                        Debug.LogFormat( "送信成功グリップ：{0}", g_message_l );
                    }
                }
                if (rightHand != null && leftHand == null)
                {
                    // サーバに文字列を送信します
                    var buffer = Encoding.UTF8.GetBytes( m_message_r );
                    m_networkStream.Write( buffer, 0, buffer.Length );
                    Debug.LogFormat( "送信成功R：{0}", m_message_r );
                }
                if (rightHand != null && leftHand != null)
                {
                    var buffer = Encoding.UTF8.GetBytes( m_message_r );
                    m_networkStream.Write( buffer, 0, buffer.Length );
                    Debug.LogFormat( "送信成功R：{0}", m_message_r );

                    buffer = Encoding.UTF8.GetBytes( m_message_l );
                    m_networkStream.Write( buffer, 0, buffer.Length );
                    Debug.LogFormat( "送信成功L：{0}", m_message_l );
                }

                count = count +1;
                Debug.LogFormat("カウント:{0}",count);

                var buffer_1 = new byte[256];
                var read = m_networkStream.Read( buffer_1, 0, buffer_1.Length );
                var message = Encoding.UTF8.GetString( buffer_1, 0, read);    
                Debug.LogFormat("受信成功:{0}", message);
            }
            catch ( Exception )
            {
                // サーバが起動しておらず送信に失敗した場合はここに来ます
                // SocketException 型だと例外のキャッチができないようなので
                // Exception 型で例外をキャッチしています
                Debug.LogError( "送信失敗" );
            }
        }
    }
//================================================================================

    
//================================================================================
    /// <summary>
    /// 破棄する時に呼び出されます
    /// </summary>
    private void OnDestroy()
    {
        // 通信に使用したインスタンスを破棄します
        // Awake 関数でインスタンスの生成に失敗している可能性もあるので
        // null 条件演算子を使用しています
        m_tcpClient?.Dispose();
        m_networkStream?.Dispose();

        Debug.Log( "切断" );
    }
//================================================================================
}