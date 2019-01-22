from threading import Thread


class NewThread(Thread):
 
    def __init__(self,func,args=()):
        super(NewThread,self).__init__()
        self.func = func
        self.args = args
 
    def run(self):
        self.result = self.func(*self.args)
 
    def get_result(self):
        try:
            return self.result
        except Exception:
            return None