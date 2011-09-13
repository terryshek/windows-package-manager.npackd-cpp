import os
import subprocess
import shutil

class BuildError(Exception):
    '''A build failed'''
    
    def __init__(self, message):
        self.message = message
        
    def __str__(self):
        return repr(self.message)

def capture_process_output_line(cmd):
    '''Captures the output of a process.'''
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, errors = p.communicate()
    return output.decode("utf-8", "strict").strip()
    
def needs_update(source, dest):
    '''Returns True if the dest file have to be re-created'''
    res = True
    if os.path.exists(source):
        res = not os.path.exists(dest) or (
                os.path.getmtime(source) >= os.path.getmtime(dest))
    else:
        res = not os.path.exists(dest)
    return res

class NpackdCLTool:
    '''NpackdCL'''
    
    def __init__(self):
        p = os.environ['NPACKD_CL']
        cl = p + '\\npackdcl.exe'
        if p.strip() == '' or not os.path.exists(cl):
            self.location = ""
        else:
            self.location = cl
        
    def add(self, package, version):
        '''Installs a package
        
        package package name like "com.test.Editor"
        version version number like "1.2.3"
        '''
        prg = "\"" + self.location + "\""
        p = subprocess.Popen(prg + " " + 
                " add --package=" + package + 
                " --version=" + version)
        err = p.wait()
        
        # NpackdCL returns 1 if a package is already installed
        #if err != 0:
        #    raise BuildError("Installation of %s %s via NpackdCL failed. Returned error code: %d" % (package, version, err))

    def path(self, package, versions):
        '''Finds an installed package
        
        package package name like "com.test.Editor"
        versions version range like "[2, 3.1)"
        '''
        return capture_process_output_line("\"" + self.location + "\" " +
                " path --package=" + package + " --versions=" + versions)
        
class Build:
    '''* Qt SDK 1.1.1
    * MinGW does not provide msi.h (Microsoft Installer interface) and the corresponding library. msi.h was taken from the MinGW-W64 project and is committed together with libmsi.a in the Mercurial repository. To re-create the libmsi.a file do the following:
    * download mingw-w32-bin_i686-mingw_20100914_sezero.zip
    * run gendef C:\Windows\SysWOW64\msi.dll 
    * run dlltool -D C:\Windows\SysWOW64\msi.dll -V -l libmsi.a
    '''

    def _build_wpmcpp(self):
        ret = True
    
        e = dict(os.environ)
        e["PATH"] = self._qtsdk + "\\mingw\\bin"
        p = subprocess.Popen("\"" + self._qtsdk + 
                "\\Desktop\\Qt\\4.7.3\\mingw\\bin\\qmake.exe\" " + 
                "wpmcpp.pro " +
                "-r -spec win32-g++ " +
                "CONFIG+=release",
                cwd="wpmcpp", env=e)
        ret = p.wait() == 0
            
        if ret:
            p = subprocess.Popen("\"" + self._qtsdk + 
                    "\\mingw\\bin\\mingw32-make.exe\" ", 
                    cwd="wpmcpp-build-desktop", env=e)
            ret = p.wait() == 0

        return ret

    def _build_msi(self):
        ret = True
    
        loc = self._npackdcl.path("com.advancedinstaller.AdvancedInstallerFreeware", "[8.4,9)")
        if loc.strip() == '':
            print('Advanced Installer [8.4, 9) was not found')
            ret = False

        if ret:
            p = subprocess.Popen(
                    "\"" + loc + "\\bin\\x86\\AdvancedInstaller.com\" " + 
                    "/build wpmcpp.aip", 
                    cwd="wpmcpp")
            ret = p.wait() == 0
        
        return ret

    def _build_npackdcl(self):
        ret = True
    
        e = dict(os.environ)
        e["PATH"] = self._qtsdk + "\\mingw\\bin"
        p = subprocess.Popen("\"" + self._qtsdk + 
                "\\Desktop\\Qt\\4.7.3\\mingw\\bin\\qmake.exe\" " + 
                "npackdcl.pro " +
                "-r -spec win32-g++ " +
                "CONFIG+=release",
                cwd="npackdcl", env=e)
        ret = p.wait() == 0
            
        if ret:
            p = subprocess.Popen("\"" + self._qtsdk + 
                    "\\mingw\\bin\\mingw32-make.exe\" ", 
                    cwd="npackdcl-build-desktop", env=e)
            ret = p.wait() == 0

        return ret

    def _build_zlib(self):
        ret = False
        
        if not os.path.exists("zlib"):
            p = self._npackdcl.path("net.zlib.ZLibSource", "[1.2.5,1.2.5]")
            if p.strip() == '':
                print('zlib 1.2.5 was not found')
            else:
                shutil.copytree(p, "zlib")
                e = dict(os.environ)
                e["PATH"] = self._qtsdk + "\\mingw\\bin"
                p = subprocess.Popen("\"" + self._qtsdk + 
                        "\\mingw\\bin\\mingw32-make.exe\" -f win32\Makefile.gcc", 
                        cwd="zlib", env=e)
                ret = p.wait() == 0
        else:
            ret = True
            
        return ret

    def _build_quazip(self):
        ret = False
        
        if not os.path.exists("QuaZIP"):
            p = self._npackdcl.path("net.sourceforge.quazip.QuaZIPSource", "[0.4.2,0.4.2]")
            if p.strip() == '':
                print('QuaZIPSource 0.4.2 was not found')
            else:
                # QuaZIP searches for -lz.dll...
                shutil.copy("zlib\\libzdll.a", "zlib\\libz.dll.a")
                
                shutil.copytree(p, "QuaZIP")
                e = dict(os.environ)
                e["PATH"] = self._qtsdk + "\\mingw\\bin"
                p = subprocess.Popen("\"" + self._qtsdk + 
                        "\\Desktop\\Qt\\4.7.3\\mingw\\bin\\qmake.exe\" " + 
                        "CONFIG+=release "
                        "INCLUDEPATH=" + self._project_path + "\\zlib " + 
                        "LIBS+=-L" + self._project_path + "\\zlib " + 
                        "LIBS+=-L" + self._project_path + "\\QuaZIP\\quazip\\release", 
                        cwd="QuaZIP", env=e)
                ret = p.wait() == 0
                
                if ret:
                    p = subprocess.Popen("\"" + self._qtsdk + 
                            "\\mingw\\bin\\mingw32-make.exe\"", 
                            cwd="QuaZIP", env=e)
                    ret = p.wait() == 0
        else:            
            ret = True
        
        return ret
                
    def _check_mingw(self):
        ret = True
        
        self._qtsdk = "C:\\QtSDK-1.1.1"
        if not os.path.exists(self._qtsdk + "\\mingw\\bin\\gcc.exe"):
            print('Qt SDK 1.1.1 not found')
            ret = False
        
        return ret
       
    def build(self):
        try:
            self._project_path = os.path.abspath("")
            
            if not self._check_mingw():
                return
                
            self._npackdcl = NpackdCLTool()
            if self._npackdcl.location == "":
                raise BuildError("NpackdCL was not found") 
            
            self._npackdcl.add("net.zlib.ZLibSource", "1.2.5")
            self._npackdcl.add("net.sourceforge.quazip.QuaZIPSource", "0.4.2")
            self._npackdcl.add("com.advancedinstaller.AdvancedInstallerFreeware", "8.4")
                
            if not self._build_zlib():
                return      
            if not self._build_quazip():
                return
            if not self._build_wpmcpp():
                return
            if not self._build_npackdcl():
                return
            if not self._build_msi():
                return
        except BuildError as e:
            print('Build failed: ' + e.message)
        
Build().build()
        