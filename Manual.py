from Functions import *

#手动执行方式
def manual():
    sln_csprojs = []
    while True:
        log()
        print("1.编译sln或csproj项目")
        print("2.生成Nuget包(csproj绝对或相对路径)")
        print("3.sln或csproj项目Sonarqube检测")
        print("4.清除当前sln或csproj文件")
        log()
        tmp = input("请输入操作序号：")
        if not tmp.isdigit():
            log("输入有误，重新输入")
            continue
        num = int(tmp)
        out_put = os.path.abspath("./output")
        if len(sln_csprojs) < 1:
            pattern = input("请输入sln或csproj匹配名：").strip()
            sln_csprojs = find_files(pattern,'.')
            if len(sln_csprojs) < 1:
                log("未在目录[%s]匹配到[%s]的文件" % pattern)
                continue
        if num == 1:
            print(sln_csprojs)
            msbuild(out_put,sln_csprojs)
        elif num == 2:
            print(sln_csprojs)
            index = int(input("请选择sln文件序号："))
            csproj_pattern = input("请输入csproj匹配名:")
            csprojs = find_csproj_path(sln_csprojs[index],csproj_pattern)
            print(csprojs)
            for csproj in csprojs:
                version = input("请输入nuget版本号(不输入则使用AssemblyInfo.cs指定)：")
                build_nuget(csproj,version,out_put)
        elif num == 3:
            print(sln_csprojs)
            key = input("请输入项目key：")
            version = input("请输入项目版本：")
            sonarqube_begin(key,version)
            msbuild(out_put,sln_csprojs)
            sonarqube_end()
        elif num == 4:
            sln_csproj = ""
        else:
            log("输入有误，重新输入")
#手动界面操作
def main():
    manual()

if __name__ == "__main__":
    main()