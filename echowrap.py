from buildbot.process import buildstep 
from buildbot.process import remotecommand 
from buildbot.status.results import FAILURE 
from buildbot.status.results import SUCCESS

class EchoWrap(buildstep.BuildStep):
    name = 'Echo Wrap'
    renderables = ['msg']
    haltOnFailure = True
    flunkOnFailure = True
   
    def __init__(self, msg, **k):
        buildstep.BuildStep.__init__(self,**k)
        self.msg = msg

    def start(self):
        cmd = remotecommand.RemoteCommand('wrap',{
            'msg':self.msg,
            '_cmdName':'com.example.test'})
        d = self.runCommand(cmd)
        d.addCallback(lambda res: self.commandComplete(cmd))
        d.addErrback(self.failed)

    def commandComplete(self, cmd):
        if cmd.didFail():
            self.descriptionDone = ["ECHO Failed (?)"]
            self.finished(FAILURE)
            return
        s = cmd.updates["pong"]
        self.step_status.setText(str(s))
        self.finished(SUCCESS)
