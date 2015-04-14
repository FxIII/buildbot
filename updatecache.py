from buildbot.process import buildstep 
from buildbot.process import remotecommand 
from buildbot.status.results import FAILURE 
from buildbot.status.results import SUCCESS
from sourcecache import SourceCachePackage

class UpdateCache(buildstep.BuildStep):
    name = 'update cache'
    renderables = ['pkg']
    haltOnFailure = True
    flunkOnFailure = True
   
    def __init__(self, pkg, **k):
        buildstep.BuildStep.__init__(self,**k)
        self.pkg = pkg

    def start(self):
        pkg = SourceCachePackage(self.pkg)
        cmd = remotecommand.RemoteCommand('updateCache',{
            '_package':pkg})
        d = self.runCommand(cmd)
        d.addCallback(lambda res: self.commandComplete(cmd))
        d.addErrback(self.failed)

    def commandComplete(self, cmd):
        if cmd.didFail():
            self.descriptionDone = ["ECHO Failed (?)"]
            self.finished(FAILURE)
            return
        self.descriptionDone = ["done"]
        self.finished(SUCCESS)

