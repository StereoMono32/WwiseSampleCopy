from waapi import WaapiClient, CannotConnectToWaapiException
from pprint import pprint


def getPro(client:WaapiClient,select_path:str):
    args = {
        "object":select_path
    }

    c = client.call("ak.wwise.core.object.getPropertyAndReferenceNames",args)
    print(c)
    return  

def getinfo_Type(client:WaapiClient,select_path:str):
    args_property = {
        "from":{"path":[select_path]}
    }
    optionAA = {
        "return":["type"]
    } 
    #print(client)
    #print(select_path)
    type_list = client.call("ak.wwise.core.object.get", args_property,options = optionAA).get("return")
    
    for item in type_list:
    # 检查字典中键 'type' 的值
        if item.get("type") == "RandomSequenceContainer":
            args_RSC={
                "from":{
                    "path": [select_path]
                }
            }
            opts_RSC={
                "return": [
                    "RandomOrSequence"
                ]
            }
            RSC_type = client.call("ak.wwise.core.object.get",args_RSC,options=opts_RSC).get("return")
            for sth in RSC_type:
                if sth.get("RandomOrSequence") == 0:
                    return "Sequence Container"
                else:
                    return "Random Container"
        else:
            return item.get("type")

    print(type_list)

def get_pathType(client:WaapiClient,path:str):
    # 拆解路径并传入 get_type 函数
    path_results = []
    sub_paths = path.split('\\')

    for i in range(len(sub_paths), 1, -1):
        sub_path = '\\'.join(sub_paths[:i])
        last_Subvalue = sub_paths[i-1]
        type_value = getinfo_Type(client,sub_path)
        path_results.append((last_Subvalue, type_value))
    
    final_result = ''
    # 从后往前遍历列表
    for pair in reversed(path_results):
        key, value = pair
        final_result += f'\\<{value}>{key}'

    start_index = final_result.find('<')
    end_index = final_result.find('>') + 1
    final_result = final_result[:start_index] + final_result[end_index:]
    
    # 打印最终结果
    return final_result


def import_AudioFromPath_SFX(client:WaapiClient,filePaths:str,projectPath:str,i):
    args_import = {
        "importOperation": "useExisting", 
        "default": {
            #导入语言
            "importLanguage": "SFX"
        },
        "imports": [
            {
                "audioFile":filePaths,
                "objectPath": f"{projectPath}{f'_{i:02}' if i != 0 else ''}"
            }
        ]
    }
    opts = {
        "platform": "Windows",
        "return": [
            "path", "name"
        ]
    }
    import_list = client.call("ak.wwise.core.audio.import", args_import, options=opts).get("objects")
    
    return import_list





def get_selectedpath(client:WaapiClient):
    
    #获取选择的object的路径
    select_list = client.call("ak.wwise.ui.getSelectedObjects",options={"return":["path"]}).get("objects")
    if select_list:
        select_path = select_list[0].get("path",{})
    else:
        return "select_path选择了根目录,请选择一个别的"
    
    #返回这个路径
    a = get_pathType(client,select_path)
    
    return a,select_path
    


#1.1补充
def getpath_Ancestors(client:WaapiClient,select_path:str):
    args_Parent = {
        "from":{
            "path":[select_path]
        },
        "transform":[
            {"select":["ancestors"]}
        ]
    }
    optionParent = {
        "return":["name","path","type","Color","OverrideColor","Volume","Lowpass","MakeUpGain","Pitch","Highpass"]
    } 
    parentsInfo = client.call("ak.wwise.core.object.get",args_Parent,options = optionParent).get("return")

    args_itself = {
        "from":{
            "path":[select_path]
        }
    }
    optionParent = {
        "return":["name","path","type","Color","OverrideColor","IsLoopingEnabled","IsLoopingInfinite","Volume","Lowpass","MakeUpGain","Pitch","Highpass"]
    } 
    itselfInfo = client.call("ak.wwise.core.object.get",args_itself,options = optionParent).get("return")

    outputInfo = itselfInfo + parentsInfo
    #value = data[0]['path']
    #print(outputInfo)

    return outputInfo



def create_object_from(client:WaapiClient,outputInfo,amount:int):
    
    exclude_keys = {'type', 'name', 'path'}

    if len(outputInfo) > 1:
        for i in range(len(outputInfo)-2, -1,-1):
            type_value = outputInfo[i]["type"]
            name_value = outputInfo[i]["name"]
            parentpath_value = outputInfo[i+1]["path"]
            path_value = outputInfo[i]["path"]
            #print("这个东西的的父级是",parentpath_value,"typebalue是",type_value,"名称是",name_value)
            if i != 0:
                crearte_object_merge(client,parentpath_value,type_value,name_value)
                
                for key, value in outputInfo[i].items():
                    if key not in exclude_keys:
                        setobjectproperty(client,path_value,key,value)

            else:
                origin_id = crearte_object_rename(client,parentpath_value,type_value,name_value)
                print(origin_id)
                for key, value in outputInfo[i].items():
                    if key not in exclude_keys:
                        setobjectproperty(client,origin_id,key,value)
                for a in range(amount-1): 
                    objectcopy(client,origin_id,parentpath_value)

        
    else:
        print("null")

    return


def crearte_object_merge(client:WaapiClient,parent_Path:str,itself_Type:str,itself_Name:str):
    args_created={
        "parent" : parent_Path,
        "type" : itself_Type,
        "name": itself_Name,
        "onNameConflict":"merge"
    }

    return client.call("ak.wwise.core.object.create",args_created)

def crearte_object_rename(client:WaapiClient,parent_Path:str,itself_Type:str,itself_Name:str):
    args_created={
        "parent" : parent_Path,
        "type" : itself_Type,
        "name": itself_Name,
        "onNameConflict":"rename"
    }
    a = client.call("ak.wwise.core.object.create",args_created).get("id")
    return a


#1.2更新设置目标的属性
def setobjectproperty(client:WaapiClient,object_id:str,property_name:str,property_value):
    args = {
        "object": object_id,
        "property": property_name,
        "value": property_value
    }
    client.call("ak.wwise.core.object.setProperty",args)
    return

def objectcopy(client:WaapiClient,object_id:str,parent_Path:str):
    args = {
        "object": object_id,
        "parent": parent_Path,
        "onNameConflict": "rename"
    }
    client.call("ak.wwise.core.object.copy",args)
    return

#1.3更新通过指定wwiseobject来创建event
def createEvent(client:WaapiClient,target_path:str,target_name:str,folder_name="GeneratedFolder"):
    args = {
        "parent": "\\Events\\Default Work Unit",
        "type": "Folder",
        "name": folder_name,
        "onNameConflict": "merge",
        "children": [
            {
                "type": "Event",
                "name": f"{target_name}_event",
                
                "children": [
                    {
                        "name": "",
                        "type": "Action",
                        "@ActionType": 1,
                        "@Target": target_path
                    }
                ]
            }
        ]
    }
    
    client.call("ak.wwise.core.object.create",args)

    
def createEvent_selectpath(client:WaapiClient,input_folderName:str):

    select_list = client.call("ak.wwise.ui.getSelectedObjects",options={"return":["path","name"]}).get("objects")
    print(select_list)
    if select_list:
        for i in range(0,len(select_list),1):
            select_path = select_list[i].get("path")
            select_name = select_list[i].get("name")
            createEvent(client,select_path,select_name,input_folderName)
        return select_path,select_name
    else:
        return 



def create_soundbank(client:WaapiClient,inputsoundbankName:str):
    
    args_create_soundbank = {
        "parent": "\\SoundBanks\\Default Work Unit", 
        "type": "SoundBank", 
        "name": inputsoundbankName, 
        "onNameConflict": "replace"
    }
    
    soundbank_info = client.call("ak.wwise.core.object.create", args_create_soundbank)
    return soundbank_info

def set_soundbank(client:WaapiClient,inputsoundbankName:str,input_folderName:str):
    args_set_inclusion = {
        "soundbank": f"\\SoundBanks\\Default Work Unit\\{inputsoundbankName}", 
        "operation": "add", 
        "inclusions": [
            {
                
                "object": f"\\Events\\Default Work Unit\\{input_folderName}", 
                "filter": [
                    "events", 
                    "structures",
                    "media"
                ]
            }
        ]
    }

    return client.call("ak.wwise.core.soundbank.setInclusions", args_set_inclusion)


def generate_soundbank(client:WaapiClient,inputsoundbankName:str):
    
    args_generate_soundbank = {
        "soundbanks": [
            {
                "name": inputsoundbankName
            }
        ],
        "writeToDisk": True
    }
    a = client.call("ak.wwise.core.soundbank.generate", args_generate_soundbank)
    print(a)
    return 

def check_select(client:WaapiClient):
    select_list = client.call("ak.wwise.ui.getSelectedObjects",options={"return":["path","name"]}).get("objects")
    print("已选择的object为:",select_list)
    return
