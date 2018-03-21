import os
import sys
import subprocess
import shutil

import DeployConfig
from Functions import *
#解析分支
def _split_branch():
    list_tmp = gitlabBranch.split("_",1)
    len_tmp = len(list_tmp)
    if len_tmp < 1:
        raise Exception(exception("分支信息【%s】有误" % list_str))
    return list_tmp

#校验标签
def _check_tag(component,project_type):
    log("开始校验标签")
    cmd_out = subprocess.Popen('git describe --tags',shell=True,stdout=subprocess.PIPE).stdout.read()
    tag_name = bytes.decode(cmd_out).split('-')[0].strip()
    #tag_name = "L_003_MEEC_BUILD_0.12.0.0_20171228"
    log(tag_name)
    if tag_name == "":
        raise Exception(exception("未获取到标签"))
    else:
        list_str = tag_name.split("_")
        if len(list_str) != 6:
            raise Exception(exception("标签信息有误（信息个数）"))
        log("标签信息")
        print("标签类型：" + list_str[0])
        print("产品代号：" + list_str[1])
        print("标签组件：" + list_str[2])
        print("标签目标：" + list_str[3])
        print("编译版本：" + list_str[4])
        print("标签日期：" + list_str[5])
        log()
        list_lable_version = list_str[4].split(".")
        if len(list_lable_version) != 4:
            raise Exception(exception("标签号必须为四位"))

        for x in list_lable_version:
            if not x.isdigit():
                raise Exception(exception("标签号必须为数字"))

        nuget_ver = list_lable_version[0] + '.' + list_lable_version[1] + '.' + list_lable_version[2]

        def __check_std(src,dst,error):
            if src.upper() != dst.upper():
                raise Exception(exception(error + dst))

        __check_std(list_str[2],component,"标签组件必须为")
        lable_type = "L"
        __check_std(list_str[0],lable_type,"标签类型必须为")
        if "CONTRACT" in project_type.upper():
            tag_type = "CONTRACT"
        else:
            tag_type = "BUILD"
        __check_std(list_str[3],tag_type,"标签目标必须为")
        log("标签校验成功")
        return tag_name,nuget_ver

def _start003script():
    log("git信息")
    print("项目：" + gitlabSourceNamespace)
    print("模块：" + gitlabSourceRepoName)
    print("分支：" + gitlabBranch)
    log()
    component,project_type = _split_branch()
    #默认msbuild输出目录
    output_path = os.path.abspath("./build/Output/" + component)
    #nuget分支处理
    if "nuget" in project_type.lower():
        #1.检查标签
        #2.编译+制作nuget包
        #3.版本校验
        #4.发布nuget服务器
        tag_name,nuget_ver = _check_tag(component,project_type)
        check_nuget(component,nuget_ver)
        sln_pattern,csproj_pattern = "*" + component + "*.sln","*" + component + "*.csproj"
        sln_path = '.'
        slns = find_slns(sln_path,sln_pattern)
        if len(slns) != 1:
            raise Exception(exception("未找到或找到多个sln文件，路径【%s】,匹配【%s】" % (sln_path,sln_pattern)))
        csproj_paths = find_csproj_path(slns[0],csproj_pattern)
        if len(slns) != 1:
            raise Exception(exception("未找到或找到多个csproj文件路径,匹配【%s】" % csproj_pattern))
        build_nuget(csproj_paths[0],nuget_ver,output_path)
        nuget_file = _check_version(output_path,tag_name,component,nuget_ver=nuget_ver)
        upload_nuget_server(nuget_file,"smee@123456","http://172.16.42.134:1000/api/v2/package")
    #release分支处理
    elif "release" in project_type.lower():
        #检查标签
        tag_name,nuget_ver = _check_tag(component,project_type)
        #sonarqube预处理
        sonarqube_begin(gitlabSourceNamespace + '_' + gitlabSourceRepoName + '_' + gitlabBranch,"1.0.0")
        #读取Config文件
        config_path = '.'
        config_pattern = "*Configuration*.xml"
        flag = True
        try:
            config_file = find_files(config_pattern,config_path)[0]
        except :
            flag = False
            log("未匹配到配置文件，使用默认方式")
        #读取到配置文件
        if flag:
            #sloution对象
            for sloution in DeployConfig.get_solutions(config_file):
                #输出目录
                output_path = os.path.abspath(sloution.Output.strip())
                sln_name = sloution.SolutionName
                log("读取配置文件成功，读取SolutionName：【%s】,输出目录为:【%s】" % (sln_name,output_path))
                #编译
                msbuild(output_path,os.path.join(sloution.SolutionPath + sloution.SolutionName))
                type = sloution.Type
                log("sln类型为：" + type)
                #配置文件生成目录
                src_path = DeployConfig.generate(config_file)
                cmd = os.path.join(g_tools_path,'rar a -r -ep1 %s.zip %s' % (component,src_path))
                #判断是服务还是插件
                if type.lower() == "module":
                    #版本校验
                    _check_version(output_path,tag_name,component,False)
                    cmd = cmd + '/'
        else:#未读取到
            sln_pattern = "*" + component + "*.sln"
            slns = find_slns('.',sln_pattern)
            isModule = True
            #编译
            msbuild(output_path,slns)
            for sln in slns:
                if "view" in sln.lower() or "gui" in sln.lower() or "plugin" in sln.lower():
                    isModule = False
            #版本校验
            if isModule:
                verifyContractDll,verifyModuleDll = _check_version(output_path,tag_name,component,False)
                cmd = g_tools_path + "/rar.exe a -ep1 " + component + ".zip Configuration " + verifyModuleDll + ' ' + verifyContractDll
            else:
                src_path = os.path.abspath("./build/Deployment/" + component)
                if not os.path.exists(src_path):
                    os.makedirs(src_path)
                    log("创建目录" + src_path)
                    pattern = "*component*.dll"
                    count = 0
                    for match in find_files(pattern,output_path):
                        count = count + 1
                        shutil.copy2(match,src_path)
                        log("复制文件：%s -> %s" % (match,src_path))
                    if count <= 0:
                        raise Exception(exception("未在路径【%s】下找到【%s】文件" % (output_path,pattern)))
                cmd = os.path.join(g_tools_path,'rar a -r -ep1 %s.zip %s' % (component,src_path))
        #sonarqube检查
        sonarqube_end()
        #打包部署包
        log("在sln目录生成部署包->%s.zip" % component)
        print(cmd_msg + cmd)
        if subprocess.call(cmd) != 0:
            raise Exception("生成失败")
        #上传starteam
        log("开始上传Starteam")
        cmd = os.path.join(g_tools_path , "ChickInToStarTeam.bat %s %s %s" % (project_type,tag_name,component))
        print(cmd_msg + cmd)
        if subprocess.call(cmd) != 0:
            raise Exception("上传Starteam失败")
    
    elif "develop" in project_type.lower():
        #编译
        sln_pattern = "*" + component + "*.sln"
        msbuild(output_path,find_slns('.',sln_pattern))

    elif "contract" in project_type.lower():
        tag_name,nuget_ver = _check_tag(component,project_type)
        sln_pattern = "*contract*" + component + "*.sln"
        msbuild(output_path,find_slns('.',sln_pattern))
    else :
        raise Exception(exception("类型【%s】不符合规则" % project_type))

#Module验证定义
def _check_version(src_path,tag_name,component,isnuget=True,nuget_path='.',nuget_ver=''):
    log("开始版本校验")
    if isnuget:
        nuget_pattern = "*" + component + '.' + nuget_ver + "*.nupkg"
        nuget_files = find_files(nuget_pattern,nuget_path)
        dll_pattern = "*contract." + component + ".dll"
        dll_files = find_files(dll_pattern,src_path)
        if len(nuget_files) < 1 :
            raise Exception(exception("未在路径%下匹配到【%s】的nupkg" % (src_path,nuget_pattern)))
        elif len(dll_files) < 1:
            raise Exception(exception("未在路径【%s】下匹配到【%s】的dll" % (src_path,dll_pattern)))
        cmd = g_tools_path + r"\VersionCompare.exe 1 %s %s %s" % (tag_name, os.path.basename(nuget_files[0]),dll_files[0])
    else:
        verifyContractDll,verifyModuleDll = "",""
        contract_pattern = "*contract." + component + "*.dll"
        contract_dlls = find_files(contract_pattern,src_path)
        module_pattern = "*module." + component + ".dll"
        module_dlls = find_files(module_pattern,src_path)
        if len(contract_dlls) < 1:
            raise Exception(exception("未在路径【%s】下找到检测到【%s】" % (src_path,contract_pattern)))
        if len(module_dlls) < 1:
            raise Exception(exception("未在路径【%s】下找到检测到【%s】" % (src_path,module_pattern)))
        cmd = os.path.join(g_tools_path,"VersionCompare.exe 2 %s %s %s" % (tag_name,contract_dlls[0],module_dlls[0]))
        print(cmd_msg + cmd)
        cmd_out = subprocess.Popen(cmd,shell = True,stdout = subprocess.PIPE)
        cmd_out_msg = bytes.decode(cmd_out.stdout.read(),encoding="gbk").strip()
        print(cmd_out_msg)
        if cmd_out.wait() != 0:
            raise Exception(exception("校验失败"))
        else:
            log("校验成功")
        if isnuget:
            return nuget_files[0]
        else:
            return contract_dlls[0],module_dlls[0]

gitlabSourceNamespace,gitlabSourceRepoName,gitlabBranch = ("" for x in range(3))
def main():
    global gitlabSourceNamespace,gitlabSourceRepoName,gitlabBranch,g_tools_path
    if len(sys.argv) == 4:
        gitlabSourceNamespace,gitlabSourceRepoName,gitlabBranch = (x for x in sys.argv[1:])
        log("脚本目录为：" + g_tools_path)
        _start003script()
    else:
        raise Exception(exception("参数错误"))

if __name__ == "__main__":
    main()