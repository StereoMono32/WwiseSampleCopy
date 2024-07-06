import json
import os
import sys

# 获取程序所在的目录
def get_current_directory():
    if getattr(sys, 'frozen', False):
        # 如果程序是被打包的，则返回打包后的可执行文件的目录
        return os.path.dirname(sys.executable)
    else:
        # 否则返回脚本所在的目录
        return os.path.dirname(os.path.abspath(__file__))

# 获取保存文件的完整路径
def get_file_path(filename):
    current_directory = get_current_directory()
    return os.path.join(current_directory, filename)

# 将路径和名字保存到文件
def save_to_file(name:str,path:str,listS,filename="saved_paths.json"):
    file_path = get_file_path(filename)

    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            data = json.load(file)
    else:
        data = {}

    data[name] = {
        "specificpath": path,
        "selectlist":listS
    }

    with open(file_path, "w") as file:
        print("文件保存到了:",file)
        json.dump(data, file, indent=4)

# 从文件中读取所有名字和对应路径
def retrieve_all_from_file(filename="saved_paths.json"):
    file_path = get_file_path(filename)

    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            #打包调试
            print("读取的文件是:",file)
            data = json.load(file)
            return data
    else:
        return {}
    

# 删除文件中特定名字的键值对
def delete_from_file(name, filename="saved_paths.json"):
    file_path = get_file_path(filename)

    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            data = json.load(file)
        
        if name in data:
            del data[name]

            with open(file_path, "w") as file:
                json.dump(data, file, indent=4)
            print(f"'{name}' has been deleted from {filename}.")
        else:
            print(f"'{name}' not found in {filename}.")
    else:
        print(f"{filename} does not exist.")

#用名字找对应的路径
def find_from_file(inputName,lpbool:bool,filename="saved_paths.json"):
    file_path = get_file_path(filename)
    
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            data = json.load(file)
        
        projectpath = {}

        if inputName in data:
            if lpbool:
                projectpath = data[inputName]["selectlist"]
            else:
                projectpath = data[inputName]["specificpath"]
            print("选择的列表是",data[inputName]["specificpath"])
        else:
            
            print(f"'{inputName}'not found in {filename}")
    else:
        
        print(f"{filename} does not exist.")   
    
    return projectpath
