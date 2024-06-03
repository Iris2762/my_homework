使用该工具前的相关环境配置：

为了实现在命令行输入指令fje -f <file_path> -s <style> -I <icon family>的功能，还需要进行以下操作
1）	在fje.py所在的目录下编写fje.bat文件（windows操作系统中的实现方法），fje.bat文件中内容如下：
 
2）	然后将fje.bat所在目录的路径存入环境变量中的系统变量
 
 
3）	修改cmd的属性，选择dejaVu Sans Mono字体，保存修改。（原因是不同字体的特殊符号宽度可能不一样，如果要实现题目要求的打印效果，则需要选择该cmd字体）
不关闭当前cmd，继续执行以下操作
 
4）	然后再在cmd中运行指令：
fje -f <file_path> -s <style> -I <icon family>
其中<file_path>可以为json文件的相对路径或者绝对路径，如果是相对路径，则必须是fje.bat文件所在目录内的路径。
<style>可以选择输入tree、rectangle或者new_type(其中new_type只是例子，未实现且没有输出)
<icon family>可以选择输入-1、0、1。-1表示不采用icon，0表示采用'♢'做中间节点的icon，'♤'做叶子结点icon,1表示'☺'做中间节点的icon,'☻'做叶子结点icon。
 
 
 
 
