import socket
import threading
import time

class Tello:
    def __init__(self):
        self.local_ip = ''
        self.local_port = 8889
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # socket for sending cmd
        self.socket.bind((self.local_ip, self.local_port))

        # thread for receiving cmd ack
        self.receive_thread = threading.Thread(target=self._receive_thread)
        self.receive_thread.daemon = True
        self.receive_thread.start()

        self.tello_ip = '192.168.10.1'
        self.tello_port = 8889
        self.tello_adderss = (self.tello_ip, self.tello_port)
        
        # port for receiving video stream
        self.local_video_port = 11111 
        
    def __del__(self):
        """Closes the local socket."""

        self.socket.close()
        self.socket_video.close()
        
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