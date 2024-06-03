import argparse
from abc import ABC, abstractmethod
from typing import List
import json

#icon symbol
icons=[['♢','♤'],['☺','☻']]
#style symbol
left_up_corner="┌─"
right_up_corner="─┐"
left_down_corner='└─'
right_down_corner="─┘"
left_T="├─"
right_T="─┤"
ver_line="│"
hor_line="─"

#抽象节点类
class Node(ABC):
    def __init__(self,_icon="",_name="",_level=0,_value="") -> None:
        self.icon=_icon#表示当前节点的icon
        self.name=_name
        self.level=_level
        self.value=""
        if _value!=None:
            if isinstance(_value,str):
                self.value=_value
            else:
                self.value=str(_value)

    @abstractmethod
    def draw(self) -> str:
        pass

#中间节点类，容器
class Container(Node):
    def __init__(self,_icon="",_name="",_level=0,_value=""):
        super().__init__(_icon,_name,_level,_value)
        self.children=[]#存储该中间节点导出的子节点

    def get_children(self)->List[Node]:
        return self.children
    
    def draw(self) -> str:
        # 节点中只输出icon和name：value。且不换行
        output_str = self.icon + self.name
        if self.value != "":
            output_str = output_str + ": " + self.value
        return output_str

    def add_child(self, child: Node) -> None:
        self.children.append(child)

    def extend_children(self, kids: List[Node]) -> None:
        self.children.extend(kids)


#叶子节点
class Leaf(Node):
    def __init__(self,_icon="",_name="",_level=0,_value=""):
        super().__init__(_icon,_name,_level,_value)

    def draw(self) -> str:
        # 节点中只输出icon和name：value。且不换行
        output_str = self.icon + self.name
        if self.value != "":
            output_str = output_str + ": " + self.value
        return output_str

# 节点的抽象工厂类
class NodeFactory(ABC):
    @abstractmethod
    def create_node(self, _icon="", _name="", _level=0, _value="") -> Node:
        pass

#中间节点container的具体工厂
class ContainerFactory(NodeFactory):
    def create_node(self, _icon="", _name="", _level=0, _value="") -> Node:
        return Container(_icon, _name, _level, _value)

#叶子节点leaf的具体工厂
class LeafFactory(NodeFactory):
    def create_node(self, _icon="", _name="", _level=0, _value="") -> Node:
        return Leaf(_icon, _name, _level, _value)
    
class JsonFileNodesCreator:
    def __init__(self,_icons_type):
        self.containerCreator = ContainerFactory()
        self.leafCreator=LeafFactory()
        self.root_node = self.containerCreator.create_node()
        self.icons_type=_icons_type#0表示第一套，1表示第二套，-1表示不使用
        self.max_length=0#存储所有节点的行输出串中最大长度
        self.space_each_level=3

    def create_all_nodes(self, data: dict) -> None:
        flag,kids_node=self.create_kid_nodes(data=data)
        if flag==0:
            print("illegal json file input")
            return
        self.root_node.extend_children(kids_node)

    def find_target_icons(self):
        container_icon=" "
        leaf_icon=" "          
        if self.icons_type!=-1:
            #使用icon
            container_icon=icons[self.icons_type][0]
            leaf_icon=icons[self.icons_type][1]
        return container_icon,leaf_icon

    def get_node_str_len(self,len_key,flag,content,level):
        length=level*self.space_each_level
        if flag==0 and content!=None:#叶子节点
            length+=len_key+2+len(str(content))#tangerine: cheap & juicy!
        else:
            length+=len_key#gala     
        return length       

    def create_node(self,key,value,level,leaf_icon,container_icon):
        #当前节点和子节点有相同的祖先,标记level为1的尾结点所在的子树中的所有节点
        flag,content=self.create_kid_nodes(data=value,level=level+1,parent_key=key)
        length=self.get_node_str_len(len(key),flag,content,level)
        if flag==0:
            #没有子节点的情况
            node=self.leafCreator.create_node(_icon=leaf_icon,_name=key,_level=level,_value=content)
        else:
            #有子节点
            node=self.containerCreator.create_node(_icon=container_icon,_name=key,_level=level)
            node.extend_children(content)   
        return length,node
        
    #返回由data创建的所有节点列表,level表示将要创建的节点的level,parent_key专门用于数组类型
    def create_kid_nodes(self,data,level=1,parent_key=""):
        items=[]
        max_len=0
        container_icon,leaf_icon=self.find_target_icons()
        if isinstance(data, dict):
            for key, value in data.items():                
                length,node=self.create_node(key,value,level,leaf_icon,container_icon)
                max_len=max(max_len,length)
                items.append(node)
        elif isinstance(data, list):
            #遍历列表中的所有元素
            for i, value in enumerate(data):
                full_key = f"{parent_key}[{i}]"
                length,node=self.create_node(full_key,value,level,leaf_icon,container_icon)
                max_len=max(max_len,length)
                items.append(node)
        else:
            #如果传入的value，不是字典也不是列表，那就是普通的值,返回0，表示返回的不是节点
            return 0,data
        max_len+=1#包括value后面的空格符,max_length只在rectangle形式输出中使用
        self.max_length=max(self.max_length,max_len)
        return 1,items        
    
    def get_root_node(self):
        return self.root_node
    
    def get_max_len(self):
        return self.max_length
    

        
#第一步：构造出所有节点，以及节点和节点之间的联系
class Printer(ABC):
    def __init__(self,_icons_type=0,max_len=0):
        self.icons_type=_icons_type#0表示第一套，1表示第二套，-1表示不使用
        self.max_length=max_len#存储所有节点的行输出串中最大长度
        self.space_each_level=3 

    @abstractmethod
    def print_node(self, node: Node, *args) -> None:
        pass


class TreePrinter(Printer):
    def __init__(self,_icons_type=0,max_len=0):
        super().__init__(_icons_type,max_len)
        #表示before_str每隔一级level会增长的长度    

    def create_kid_beforestr(self,before_str,node_name,last_kid):
        #构造子节点的before_str
        kid_before_str=before_str
        if node_name!="":#根节点的子节点的before_str为空，不需要构造
            if last_kid:
                kid_before_str+=self.space_each_level*" "
            else:
                kid_before_str+=ver_line
                kid_before_str+=(self.space_each_level-1)*" "
        return kid_before_str
    
    def print_node_outputstr(self,node_level,before_str,last_kid,node_draw):
        if node_level>0:#根节点不打印自身
            output_str=before_str
            if last_kid:
                output_str+=left_down_corner
            else:
                output_str+=left_T
            output_str+=node_draw
            print(output_str)
              
    def print_kid_nodes(self,node,before_str,last_kid):
        if hasattr(node,"children") is False:
            #叶子结点，结束
            return
        kid_before_str=self.create_kid_beforestr(before_str,node.name,last_kid)
        #打印子节点
        kids=node.get_children()
        for i,kid in enumerate(kids):
            if i==len(kids) - 1:
                self.print_node(kid,True,kid_before_str)
            else:
                self.print_node(kid,False,kid_before_str)

    #打印当前节点与其子节点
    #node是当前需要打印的节点，last_kid表示该节点是其父节点的最后一个子节点，before_str在父节点打印时被构造出来，直接打印即可
    def print_node(self,node,last_kid=False,before_str=""):
        #打印当前节点
        self.print_node_outputstr(node.level,before_str,last_kid,node.draw())
        #打印子节点
        self.print_kid_nodes(node,before_str,last_kid)
        

class RectanglePrinter(Printer):
    def __init__(self,_icons_type=0,max_len=0):
        super().__init__(_icons_type,max_len)
        self.extern_row_len=5

    def create_node_beforestr(self,level,last_row):
        before_str=""
        #生成before_str
        if last_row==False:
            before_str+=(ver_line+"  ")*(level-1)
        else:
            before_str+=(left_down_corner+hor_line)*(level-1)    
        return before_str 

    def create_node_middlestr(self,first_row,last_row,node_draw):
                #生成middle_str
        middle_str=""
        if first_row:
            middle_str+=left_up_corner+node_draw+" "
        elif last_row:
            middle_str+=left_down_corner+node_draw+" "
        else:
            middle_str+=left_T+node_draw+" "
        return middle_str
    
    def create_node_afterstr(self,len_output_str,first_row,last_row):
        #生成last部分,需要控制输出字符串的总长度为max_length+extern_row_len+2,2为每行末尾输出符号的长度
        after_str=(self.max_length-len_output_str+self.extern_row_len)*hor_line
        if first_row:
            after_str+=right_up_corner
        elif last_row:
            after_str+=right_down_corner
        else:
            after_str+=right_T
        return after_str
    
    def print_kid_nodes(self,node,may_last_row):
        #打印子节点
        if hasattr(node,"children") is False:
            #叶子结点，结束
            return
        kids=node.get_children()
        #may_last_row表示当前节点之前的祖先节点是否全部为最后一个子节点
        for i,kid in enumerate(kids):
            kid_may_last_row=may_last_row
            if i==0 and node.level==0:
                kid_first_row=True
            else:
                kid_first_row=False
            if i<len(kids)-1:
                kid_may_last_row=False
            self.print_node(kid,kid_first_row,kid_may_last_row)

    def print_node_outputstr(self,node,first_row,may_last_row):
        last_row=(not (hasattr(node,"children"))) and may_last_row
        if node.level>0:
            output_str=self.create_node_beforestr(node.level,last_row)
            output_str+=self.create_node_middlestr(first_row,last_row,node.draw())
            output_str+=self.create_node_afterstr(len(output_str),first_row,last_row)
            #进行当前节点的输出
            print(output_str)

    #first_row标记当前节点是否为level为1的节点中的第一个，这种信息在其父节点中决定
    #may_last_row标记当前节点之前所有的祖先节点是否均为其兄弟节点中最后一个节点
    def print_node(self,node,first_row=False,may_last_row=True):
        #打印当前节点
        self.print_node_outputstr(node,first_row,may_last_row)
        #打印子节点
        self.print_kid_nodes(node,may_last_row)

class NewtypePrinter(Printer):
    def __init__(self,_icons_type=0,max_len=0):
        super().__init__(_icons_type,max_len)

    def print_node(self,node,first_row=False,may_last_row=True):
        #concrete achieve code here
        return 

# printer的抽象工厂类
class PrinterFactory(ABC):
    @abstractmethod
    def create_printer(self,_icons_type=0,max_len=0) -> Printer:
        pass

#tree风格打印机的具体工厂
class TreePrinterFactory(PrinterFactory):
    def create_printer(self,_icons_type=0,max_len=0) -> Printer:
        return TreePrinter(_icons_type,max_len)

#rectangle风格的具体工厂
class RectanglePrinterFactory(PrinterFactory):
    def create_printer(self,_icons_type=0,max_len=0) -> Printer:
        return RectanglePrinter(_icons_type,max_len)

#rectangle风格的具体工厂
class NewtypePrinterFactory(PrinterFactory):
    def create_printer(self,_icons_type=0,max_len=0) -> Printer:
        return NewtypePrinter(_icons_type,max_len)
    
class FunnyJsonExploer:
    def _load(self, file_path: str) -> dict:
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data

    def show(self, printer_type: str, icons_type: int, data: dict) -> None:
        # 先创建节点
        nodes_creator=JsonFileNodesCreator(icons_type)
        nodes_creator.create_all_nodes(data)
        root_node=nodes_creator.get_root_node()
        max_len=nodes_creator.get_max_len()    
        # 根据输入参数选择创建不同风格的打印机    
        printer = None
        if printer_type == "tree":
            printer_creator=TreePrinterFactory()
            printer = printer_creator.create_printer(icons_type,max_len)
        elif printer_type == "rectangle":
            printer_creator=RectanglePrinterFactory()
            printer = printer_creator.create_printer(icons_type,max_len)
        elif printer_type=="new_type":
            printer_creator=NewtypePrinterFactory()
            printer = printer_creator.create_printer(icons_type,max_len)            
        # 再打印输出
        printer.print_node(root_node)

def main():
    parser = argparse.ArgumentParser(description="Funny JSON Explorer")
    parser.add_argument("-f", "--file", required=True, help="Path to the JSON file")
    parser.add_argument("-s", "--style", required=True, choices=["tree", "rectangle","new_type"], help="Style to display the JSON")
    parser.add_argument("-i", "--icon", type=int, default=0, choices=[-1,0, 1], help="Icon family to use (-1 or 0 or 1)")

    args = parser.parse_args()

    fje = FunnyJsonExploer()
    data = fje._load(args.file)
    fje.show(args.style, args.icon, data=data)


if __name__ == "__main__":
    main()