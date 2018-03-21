import os
import glob
import fnmatch  
import sys
import subprocess
import multiprocessing

#nuget包上传服务器
def upload_nuget_server(file_path,secret_key,server_url):
    log("开始上传Nuget服务器")
    cmd = r"NuGet.exe push %s %s -Source %s" % (file_path,secret_key,server_url)
    print(cmd_msg + cmd)
    if subprocess.call(cmd) != 0:
        raise Exception("上传Nuget服务器失败")

#通过sln文件查找csproj文件相对路径
def find_csproj_path(sln_file_path,csproj_pattern):
    sln_file = open(sln_file_path,encoding= 'utf8')
    try:
        list_tmp = sln_file.read().split('"')
        list_csproj_path = fnmatch.filter(list_tmp,csproj_pattern)
        if len(list_csproj_path) < 1 or list_csproj_path[0].strip() == "":
            raise Exception(exception("未从文件%s匹配到 %s csproj路径" % (sln_file_path,csproj_pattern)))
        return list_csproj_path
    except Exception as e:
        raise e
    finally:
        sln_file.close()

#获取路径下所有匹配的sln
def find_slns(filepath,pattern):
    list_sln = find_files(pattern, filepath)
    if len(list_sln) < 1:
        raise Exception(exception("未以[%s]方式匹配到sln文件" % pattern))
    log("找到路径下所有sln文件：")
    print(list_sln)
    return list_sln

#文件匹配
def find_files(pattern,path, patternsep=os.pathsep,pathsep=os.pathsep):
    list_tmp = []
    for path_tmp in path.split(pathsep):
        for pattern_tmp in pattern.split(patternsep):
            list_tmp+=glob.glob(os.path.join(path_tmp, pattern_tmp))
    return list_tmp

#日志信息
def log(msg=''):
    symbol = '#' * 30
    if msg.strip() == "":
        print(symbol + msg + symbol)
    else:
        print(symbol + '【 ' + msg + ' 】' + symbol)

#异常信息
def exception(msg):
    return "错误：" + msg

#sonarqube检测
def sonarqube_begin(key,version):
    log("开始sonarqube检测")
    cmd = os.path.join(g_tools_path , r"sonar-scanner-msbuild-3.0.2.656\SonarQube.Scanner.MSBuild.exe begin /k:%s /n:%s /v:%s" % (key,key,version))
    print(cmd_msg + cmd)
    if subprocess.call(cmd) != 0:
        raise Exception(exception("执行失败"))

#sonarqube检测
def sonarqube_end():
    cmd = g_tools_path + r"\sonar-scanner-msbuild-3.0.2.656\SonarQube.Scanner.MSBuild.exe end"
    if subprocess.call(cmd) != 0:
        raise Exception(exception("sonarqube检测失败"))
    log("sonarqube检测完成")

#制作nuget包
def build_nuget(csproj,nuget_ver,output):
    restore_nuget(csproj)
    log("执行打包nuget")
    if nuget_ver.strip() != "":
        cmd = "NuGet.exe pack %s -Version %s -Build -Properties Configuration=Release;Platform=x86;OutDir=%s" % (csproj,nuget_ver,output)
    else:
        log("未指定nuget版本,使用AssemblyInfo.cs指定")
        cmd = "NuGet.exe pack %s -Build -Properties Configuration=Release;Platform=x86;OutDir=%s" % (csproj,output)
    print(cmd_msg + cmd)
    if subprocess.call(cmd) != 0:
        raise Exception(exception("打包nuget失败"))

#RestoreNuget
def restore_nuget(csproj):
    log("开始执行Nuget Restore")
    cmd = r"NuGet.exe restore -ConfigFile %s\Nuget.config -Nocache %s -PackagesDirectory packages" % (g_tools_path,csproj)
    print(cmd_msg + cmd)
    if subprocess.call(cmd) != 0:
        raise Exception(exception("Nuget Restore执行失败"))

def check_nuget(nuget,version):
    cmd = r"NuGet.exe list -ConfigFile %s\Nuget.config %s" % (g_tools_path,nuget)
    print(cmd_msg + cmd)
    cmd_out = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout.read()
    str = bytes.decode(cmd_out).strip()
    if version in str and nuget in str :
        log("警告：Nuget包已经存在")
        subprocess.call("exit 1")

#MSbuild编译，需要设置好环境变量
def msbuild(out_dir,*slns):
    list_slns = []
    for x in slns:
        if isinstance(x,list):
            list_slns.extend(x)
        else:
            list_slns.append(x)
    list_p_tmp = []
    for sln in list_slns:
        restore_nuget(sln)
        p = multiprocessing.Process(target=_msbuild,args=(out_dir,sln,))
        p.daemon = True
        p.start()
        list_p_tmp.append(p)
    for p in list_p_tmp:#等待子进程执行
        p.join()
    for p in list_p_tmp:#子进程发生错误则主进程抛出异常
        if p.exitcode != 0:
            raise Exception("MSbuild执行失败")

def _msbuild(out_dir,sln):
        log("开始执行Msbuild")
        cmd = "msbuild.exe %s /t:rebuild /p:Platform=x86;Configuration=Release;OutDir=%s" % (sln,out_dir)
        print(cmd_msg + cmd)
        if subprocess.call(cmd) != 0:
            raise Exception(exception("MSbuild执行失败"))

g_tools_path = os.path.dirname(sys.argv[0])
cmd_msg = "执行命令："
def main():
    file_list = find_files("*.py",".")
    a = 0

if __name__ == "__main__":
    main()