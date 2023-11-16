import pygame

class keyborad:
    def __init__(self):
        pygame.init()
        win=pygame.display.set_mode((400,400))
        
    
    def getKey(self,keyname):
        ans=False
        for event in pygame.event.get():pass
        keyInput=pygame.key.get_pressed()
        mykey=getattr(pygame,'K_{}'.format(keyname))
        print('K_{}'.format(keyname))
        if keyInput[mykey]:
            ans = True
        pygame.display.update() 
        return ans
  
  
    def getKeyInput(self):
        
        if self.getKey("w"):
            return "rc 0 50 0 0"
        elif self.getKey("s"):
            return "rc 0 -50 0 0"
        elif self.getKey("a"):
            return "rc -50 0 0 0"
        elif self.getKey("d"):
            return "rc 50 0 0 0"            
        elif self.getKey("8"):
            return "rc 0 0 50 0"
        elif self.getKey("5"):
            return "rc 0 0 -50 0"           
        elif self.getKey("4"):
            return "rc 0 0 0 -50"
        elif self.getKey("6"):
            return "rc 0 0 0 50"        
        elif self.getKey("z"):
            return "takeoff"
        elif self.getKey("x"):
            return "land"
        else:
            pass