from khl import Message, Bot
from market import *
import logging
import json


# 用 json 读取 config.json，装载到 config 里
# 注意文件路径，要是提示找不到文件的话，就 cd 一下工作目录/改一下这里
with open('./config/config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# 用读取来的 config 初始化 bot，字段对应即可
bot = Bot(token=config['token'])


# bot响应
@bot.command(name='mitem')
async def mitem(msg: Message, item_name: str, world_name: str):
    ans = ""
    command_msg = "item" + " " + item_name.strip() + " " + world_name.strip()
    command_seg = command_msg.split(" ")
    while "" in command_seg:
        command_seg.remove("")

    if len(command_seg) == 1 or command_seg[1].lower() == "help":
        ans = """/mitem $name $server: 查询$server服务器的$name物品交易数据
    Powered by https://universalis.app"""
    elif command_seg[1].lower() == "upload":
        ans = """您可以使用以下几种方式上传交易数据：
    0.如果您使用咖啡整合的ACT，可以启用抹茶插件中的Universalis集成功能 http://url.cn/a9xaUIKs 
    1.如果您使用过国际服的 XIVLauncher，您可以使用国服支持的Dalamud版本 https://url.cn/6L7nD0gF
    2.如果您使用过ACT，您可以加载ACT插件 UniversalisPlugin https://url.cn/TEY1QKKV
    3.如果您想不依赖于其他程序，您可以使用 UniversalisStandalone https://url.cn/TEY1QKKV
    4.如果您使用过Teamcraft客户端，您也可以使用其进行上传
    Powered by https://universalis.app"""
    else:
        ans = handle_command(command_seg)

    ans = ans.strip()
    await msg.reply(f'{ans}')


# 输出日志
logging.basicConfig(level='DEBUG')


# 机器人起跑线
bot.run()


