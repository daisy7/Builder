from xml.dom.minidom import parse
import shutil
import os
import Functions

#异常信息
def _exception(msg):
    return "配置文件错误：" + msg

"""solution对象类"""
class Solution(object):
    def __init__(self, **kwargs):
        self.Key = ""
        self.SolutionName = ""
        self.SolutionPath = ""
        self.Output = ""
        self.Type = ""
        self.Preprocessor = ""
        return super().__init__(**kwargs)

def get_solutions(config_file):
    DomTree = parse(config_file)
    try:
        Configuration = DomTree.documentElement
    except:
        raise Exception(_exception("配置文件路径有误"))
    solutions = []
    for Solution_Node in Configuration.getElementsByTagName("BuildSolutions")[0].getElementsByTagName("Solution"):
        solution = Solution()
        solution.Key = _getFirstChildNodes(Solution_Node,"Key")
        solution.SolutionName = _getFirstChildNodes(Solution_Node,"SolutionName")
        solution.SolutionPath = _getFirstChildNodes(Solution_Node,"SolutionPath")
        solution.Output = _getFirstChildNodes(Solution_Node,"Output",True)
        solution.Type = _getFirstChildNodes(Solution_Node,"Type",True)
        solution.Preprocessor = _getFirstChildNodes(Solution_Node,"Preprocessor")
        solutions.append(solution)
    return solutions

def generate(config_file):
    src_path = ""
    DomTree = parse(config_file)
    try:
        Configuration = DomTree.documentElement
    except:
        raise Exception(_exception("配置文件路径有误"))
    for Deployment in Configuration.getElementsByTagName("Deployment"):
        for Folder in _getFirstLevelChildNodes(Deployment,"Folders"):
            for Folder in Folder.getElementsByTagName("Folder"):
                FolderName = Folder.getElementsByTagName("FolderName")[0].childNodes[0].data
                FolderPath = Folder.getElementsByTagName("FolderPath")[0].childNodes[0].data
                if src_path == "":
                    src_path = FolderPath
                if not os.path.exists(FolderPath):
                    os.makedirs(FolderPath)
                    Functions.log("创建目录" + FolderPath)
                for copys in _getFirstLevelChildNodes(Folder,"Copy"):
                    SourcePath = _getFirstChildNodes(copys,"SourcePath")
                    for item in copys.getElementsByTagName("Items"):
                        for item in item.getElementsByTagName("Item"):
                            count = 0
                            filename = _getFirstLevelChildNodes(item,"ItemFile")[0].childNodes[0].data
                            for match in Functions.find_files(filename,SourcePath):
                                count = count + 1
                                shutil.copy2(match,FolderPath)
                                Functions.log("复制文件：%s -> %s" % (match,FolderPath))
                            if count <= 0:
                                Functions.log("警告：未在路径【%s】下匹配到【%s】文件" % (SourcePath,filename))
    Functions.log("目录结构成功生成%s" % src_path)
    return src_path

def _getFirstChildNodes(node,tag_name,is_necessary=False):
    tmp = node.getElementsByTagName(tag_name)
    if len(tmp) > 0:
        tmp = tmp[0].childNodes
        if len(tmp) > 0:
            return  tmp[0].data
    else:
        if is_necessary:
            raise Exception(_exception("必须存在标签<" + tag_name + ">" + "或值不能为空"))
        else:
            Functions.log("配置文件警告：不存在标签<" + tag_name + ">" + "或值为空")
    return ""

def _getFirstLevelChildNodes(node,tag_name):
    nodes = []
    for i in range(node.childNodes.length):
        if node.childNodes[i].nodeName == tag_name:
            nodes.append(node.childNodes[i])
    return nodes

def main():
    config_pattern = "*Configuration*.xml"
    config_file = Functions.find_files(config_pattern,".")[0]
    src_path = generate(config_file)
    
if __name__ == "__main__":
    main()