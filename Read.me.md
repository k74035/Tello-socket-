import socket
import threading
import time
import cv2

### Tello 클래스 생성
class Tello:

## Tello 생성자 함수

    def __init__(self):
# tello의 상태를 나타내고 제어하기 위한 변수들
        self.frame = None  # numpy array BGR -- current camera output frame
        self.response = None  
        self.running = True

# 양방향 통신을 위한 IP주소와 PORT 주소
        self.local_ip = ''
        self.local_port = 8889
        self.tello_ip = '192.168.10.1'
        self.tello_port = 8889
        self.local_video_port = 11111 

        self.local_address = (self.local_ip, self.local_port)
        self.tello_adderss = (self.tello_ip, self.tello_port)

# 제어와 비디오 처리를  위한 소켓(통신객체) 생성
# 제어는 메인 스레드에서 처리하며 비디오는 보조스레드를 생성하여 처리한다.
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # socket for sending cmd
        self.socket.bind((self.local_ip, self.local_port))  
        self.socket_video = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # socket for receiving video stream
        self.socket_video.bind((self.local_ip, self.local_video_port))

# local 장치로 부터 텔로에 명령을 보내는 것은 메인 스레드이고 Tello로부터 상태를 수신 하는 것은 receive_thread를 통해 받는다.
        # thread for receiving cmd ack
        self.receive_thread = threading.Thread(target=self._receive_thread)
        self.receive_thread.daemon = True
        self.receive_thread.start()
        
        # thread for receiving videos
        # video를 쓰지 않는 코드라면 주석 처리 가능

# Tello로부터 비디오 정보를 receive_video_thread를 통해 제공받는다. 
        self.receive_video_thread = threading.Thread(target=self._receive_video_thread)
        self.receive_video_thread.daemon = True
        self.receive_video_thread.start()
 
        # to receive video -- send cmd: command, streamon
        self.socket.sendto(b'command', self.tello_address)
        print ('sent: command')
        self.socket.sendto(b'streamon', self.tello_address)
        print ('sent: streamon')


** 간단하게 생각하면 드론 제어의 명령 송신은 메인 스레드, 드론 제어 관련된 상태정보는 receive_thread(보조스레드), 
드론의 비디오 정보는 receive_video_thread(보조스레드) 에서 받으니 총 3개의 스레드가 돌아가는 상태이다. **


## Tello 함수 

    def __del__(self):
        """Closes the local socket."""
        self.socket.close()
        self.socket_video.close()
        
    def terminate(self):
        self.running = False
        self.video.release()
        cv2.destroyAllWindows()
        
    def read(self):
        """Return the last frame from camera."""
        if self.is_freeze:
            return self.last_frame
        else:
            return self.frame
        
    def send_command(self, command):
        # Send commnad to Tello
        self.socket.sendto(command.encode('utf-8'), self.tello_adderss)
        # print command and tello_ip
        print('sending command: %s to %s' % (command, self.tello_ip))

    def _receive_thread(self):
        #Listen to responses from the Tello. (Runs as a thread)
        while True:
            try:
                self.response, ip = self.socket.recvfrom(1024)
                print(self.response)
            except socket.error as exc:
                print("err")
                
    def _receive_video_thread(self):
        # Listen to responses video data from the Tello. (Runs as a thread)
        # Creating an object(video) that receives frames from Tello (->opencv)
        self.video = cv2.VideoCapture("udp://@0.0.0.0:11111")
        while self.running:
            try:
                ret, frame = self.video.read()
                if ret:
                    cv2.imshow('Tello', frame)
                cv2.waitKey(1)
            except Exception as err:
                print(err)
                
                
                
                
    def takeoff(self):
        return self.send_command('takeoff')
    
    
    def get_battery(self):
        """Returns percent battery life remaining.

        Returns:
            int: Percent battery life remaining.

        """
        
        battery = self.send_command('battery?')

        try:
            battery = int(battery)
        except:
            pass

        return battery
    
    def stop(self):
        print('stop')
        self.recvThread.terminate()
        pass

                    
# self._receive_thread 메소드를 대상으로 하는 스레드 객체를 생성합니다. 즉, _receive_thread 메소드가 스레드에서 실행될 함수로 설정됩니다.
# self.receive_thread.daemon = True:
# 이 부분은 해당 스레드를 데몬 스레드로 설정합니다. 데몬 스레드는 메인 프로그램이 종료될 때 함께 종료되는 특별한 종류의 스레드입니다. 여기서는 프로그램이 종료될 때 모든 백그라운드 스레드를 함께 종료하도록 하기 위해 사용됩니다.
# self.receive_thread.start():
> 스레드를 시작합니다. 이로써 _receive_thread 메소드가 백그라운드에서 독립적으로 실행되며, 드론으로부터 오는 응답을 지속적으로 수신합니다.
이러한 구조를 통해 메인 프로그램은 다른 작업을 수행하면서도 백그라운드에서 드론으로부터의 응답을 지속적으로 처리할 수 있게 됩니다.


# open cv 사용법 
```
https://deep-learning-study.tistory.com/107
https://inhovation97.tistory.com/51
```
> opencv에서 많이 쓰는 함수들이 깔끔하게 정리 되어있다 참고하자

```
cap = cv2.VideoCapture(0) # local의 카메라 객체 생성
cap = cv2.VideoCapture('video1.mp4') # 동영상 여는 객체 생성
cv2.VideoCapture.isOpened() -> retval # 비디오 캡쳐 준비되었는지 확인
cv2.VideoCapture.read(image=None) -> retval, image # 프레임 받아오기
```

# Plots the detection results on an input RGB image. Accepts a numpy array (cv2) or a PIL Image.