import socket
import threading
import motion
import cv2
import keyboard

# 상태 정보 활용(계산) 메인 스레드 
# 비디오 정보 수신 recieve_video_thread
# 드론 제어 송신 control_thread

class Tello:
    def __init__(self):
        
        self.text = None
        self.frame = None  # numpy array BGR -- current camera output frame
        self.response = None  
        self.running = True
        self.video = cv2.VideoCapture("udp://@0.0.0.0:11111") # video object supported by cv2 
        
        self.local_ip = ''
        self.local_port = 8889
        self.tello_ip = '192.168.10.1'
        self.tello_port = 8889
        self.local_video_port = 11111 
        
        self.local_address = (self.local_ip, self.local_port)
        self.tello_adderss = (self.tello_ip, self.tello_port)
        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # socket for sending cmd
        self.socket.bind((self.local_ip, self.local_port))  
        self.socket_video = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # socket for receiving video stream
        self.socket_video.bind((self.local_ip, self.local_video_port))
        
        '''
        # thread for receiving cmd ack
        self.receive_thread = threading.Thread(target=self._receive_thread)
        self.receive_thread.daemon = True
        self.receive_thread.start()
        '''
        
        # thread for receiving videos
        # video를 쓰지 않는 코드라면 주석 처리 가능
        self.receive_video_thread = threading.Thread(target=self._receive_video_thread)
        self.receive_video_thread.daemon = True
        self.receive_video_thread.start()
 
        # to receive video -- send cmd: command, streamon
        # 'command'라는 문자열을 보내는 역할을 합니다. Tello 드론은 이 문자열을 특별한 명령으로 인식하고, 이후에 드론은 명령을 받을 수 있는 상태로 전환됩니다.
        self.socket.sendto(b'command', self.tello_address)
        print ('sent: command')
        self.socket.sendto(b'streamon', self.tello_address)
        print ('sent: streamon')
        
    def __del__(self):
        """Closes the local socket."""
        self.socket.close()
        self.socket_video.close()
        
    def terminate(self):
        self.running = False
        self.video.release()
        cv2.destroyAllWindows()
        
        
    def myStop(self):
        print('myStop')
        self.terminate()
        pass
    
    def send_command(self, command):
        # Send commnad to Tello
        self.socket.sendto(command.encode('utf-8'), self.tello_adderss)
        # print command and tello_ip
        print('sending command: %s to %s' % (command, self.tello_ip))

    def send_drone(self,msg):
        self.send_command(self, msg)
        
    '''
    def _receive_thread(self):
        # 제어 스레드 함수
        """Listen to responses from the Tello.
        Runs as a thread, sets self.response to whatever the Tello last returned."""
        while True:
            try:
                self.response, ip = self.socket.recvfrom(3000)
                #print(self.response)
            except socket.error as exc:
                print ("Caught exception socket.error : %s" % exc)
    '''
# 비디오 스레드 함수
    def _receive_video_thread(self):
        ''' Listen to responses video data from the Tello. (Runs as a thread) 
        Creating an object(video) that receives frames from Tello (->opencv)
        tello공식 깃허브에서는 recvfrom을 통해 비디오 스레드 통신하지만 간단하게 cv2에서 지원하는 것으로 변경한 듯 '''
        while self.running:
            try:
                ret, frame = self.video.read()
                if ret:
                    cv2.imshow('Tello', frame)
                cv2.waitKey(1)
            except Exception as err:
                print(err)
    
# hand motion 제어            
    def vid_motion(self):
        while self.running:
            ''' frame으로 인해 렉걸린다면 2프레임당 한번씩 모션을 인식하겠다.
            try:
                ret, frame = self.video.read()
                count= (count+1)%2
                if ret and count == 0:
                    self.text = motion.show(frame)
            except Exception as err:
                print(err)
            '''
            self.text = motion.show(self.frame)
            
    def vid_motion_control(self):
        while self.running:
            if self.text == "come":
                self.send_drone("rc 0 30 0 0")
            elif self.text == "away":
                self.send_drone("rc 0 -30 0 0")
            elif self.text == "spin":
                self.send_drone("curve 55 55 0 0 110 0 50")
            else:
                pass

# 키보드 제어
    def keyboard_control(self):
        while self.running:
            value = keyboard.getKeyInput(self)
            if value:
                self.send_drone(value)

