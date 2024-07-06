import SavePath
from waapi import WaapiClient, CannotConnectToWaapiException
import SthTry
import tkinter as tk
from tkinter import filedialog

def open_file_dialog():
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口

    file_paths = filedialog.askopenfilenames(
        title="选择WAV文件",
        filetypes=[("WAV Files", "*.wav")]
    )

    file_paths = root.tk.splitlist(file_paths)


    if file_paths:
        print("选择的文件:")
        for file_path in file_paths:
            print(file_path)

        user_input = input("请输入模板名: ")
        confirm = input("确认设置吗？(yes/no): ").lower()

        if confirm == 'yes':
            projectpath = SavePath.find_from_file(user_input,False)
            if projectpath:
                for i,file_path in enumerate(file_paths,start=0):
                    
                    SthTry.import_AudioFromPath_SFX(client,file_path,projectpath,i)
            else:
                print("不存在对应模板命名，设置已取消。")
        else:
            print("设置已取消。")
    else:
        print("未选择文件，设置已取消。")



def create_bylist():
    user_input = input("请输入模板名: ")
    confirm = input("确认设置吗？(yes/no): ").lower()


    if confirm == 'yes':

        while True:
            amount_str = input("请输入需要生成的数量 (默认为1):") or "1"  # 默认为1
            if amount_str.isdigit():
                amount = int(amount_str)
                if amount > 0:
                    break
                else:
                    print("请输入一个大于0的整数。")
            else:
                print("请输入一个整数。")

        projectpath = SavePath.find_from_file(user_input,True)
        SthTry.create_object_from(client,projectpath,amount)
    else:
        print("设置已取消")

    return






# 主程序逻辑
if __name__ == "__main__":
    while True:
        try:
            with WaapiClient() as client:
                print("1. 生成Wwise模板路径")
                print("2. 保存Wwise模板路径")
                print("3. 查看所有保存的Wwise模板路径")
                print("4. 删除保存的字符串")
                print("5. 通过指定模板路径批量生成对应Wwiseobject")
                print("6. 通过指定模板路径批量导入wav文件(需确保末尾为sfx或者vocal)")
                print("7. 通过sfx自动生成event以及soundbank")
                print("8. 退出")


                choice = input("请选择一个操作: ")

                if choice == "1":
                    generatedpath_Wwise,select_infom = SthTry.get_selectedpath(client)
                    listS = SthTry.getpath_Ancestors(client,select_infom)
                    print(f"生成的Wwise路径: {generatedpath_Wwise}")


                elif choice == "2":
                    name = input("请输入名字来保存字符串: ")
                    SavePath.save_to_file(name,generatedpath_Wwise,listS)
                    
                    print(f"Wwise路径已保存为: {name}")

                elif choice == "3":
                    data = SavePath.retrieve_all_from_file()
                    for name, data_dict in data.items():
                        specificpath = data_dict["specificpath"]
                        print(f"Name: {name}, 具体路径:{specificpath}")

                elif choice == "4":
                    name = input("请输入要删除的名字: ")
                    SavePath.delete_from_file(name)

                elif choice == "5":
                    create_bylist()
                
                elif choice == "6":
                    open_file_dialog()
                
                elif choice == "7":
                    SthTry.check_select(client)
                    generate_confirm = input("确认是这些吗?(yes/no):")
                    if generate_confirm == "yes":
                        input_foldername = input("请输入event生成位置的的文件夹名:")
                        SthTry.createEvent_selectpath(client,input_foldername)

                        soundbank_confirm = input("是否要生成soundbank(yes/no):").lower()
                        if soundbank_confirm == "yes":
                            input_soundbankName = input("请输入soundbank名:")
                            SthTry.create_soundbank(client,input_soundbankName)
                            SthTry.set_soundbank(client,input_soundbankName,input_foldername)
                            SthTry.generate_soundbank(client,input_soundbankName)
                        else:
                            print("返回上一步")
                    else:
                        print("返回上一步")

                elif choice == "8":
                    print("退出程序")
                    break

                else:
                    print("无效选择，请重新选择。")

        except CannotConnectToWaapiException:
            print("Could not connect to Waapi: Is Wwise running and Wwise Authoring API enabled?")
