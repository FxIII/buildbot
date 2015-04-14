import sys
import os
import tempfile,tarfile
class SourceCache:
    base = "ext/_cache"
    @classmethod
    def findPackage(cls,name):
        if name == "": return False
        current = cls.base
        chunks= name.split(".")
        for i in chunks[:-1]:
            current = os.path.join(current,i)
            if not os.path.exists(current):
                return False
            if os.path.exists(os.path.join(current,"__init__.py")):
                return False
        current = os.path.join(current,chunks[-1])
        if not os.path.exists(os.path.join(current,"__init__.py")):
            return False
        return current
    @classmethod
    def packPackage(cls,package,root=None,prefix=False):
        path = cls.findPackage(package)
        if not path: return False
        if root is None:
            root = path[len(cls.base):]
        archname = root  if not prefix else root+path[len(cls.base):]
        tmp = tempfile.TemporaryFile()
        tar = tarfile.TarFile(fileobj=tmp,mode="w")
        tar.add(path,arcname=archname)
        tar.close()
        return tmp
    @classmethod
    def checksum(cls,package):
        path = cls.findPackage(package)
        if not path: return False
        md=max(os.stat(p).st_mtime for p,d,f in os.walk(path))
        mf=max(os.stat(os.path.join(p,j)).st_mtime for p,d,f in os.walk(path) for j in f)
        return max(md,mf)

from twisted.spread import pb
class SourceCachePackage(pb.Referenceable):
    def __init__(self,pkg):
        self.pkg = pkg
        self.f = None
    def remote_isValid(self):
        return SourceCache.findPackage(self.pkg) is not False
    def remote_checksum(self):
        return SourceCache.checksum(self.pkg)
    def remote_openFile(self,root=None,prefix=False):
        self.f = SourceCache.packPackage(self.pkg,root,prefix)
        self.f.seek(0)
        return self.f
    def remote_read(self,bytes=2048):
        if self.f is None:
            self.remote_openFile()
        return self.f.read(bytes)

