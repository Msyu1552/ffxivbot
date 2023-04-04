from difflib import SequenceMatcher
import requests
import time
import re


# 本地化服务器名称
def localize_world_name(world_name):
    world_dict = {
        "HongYuHai": "红玉海",
        "ShenYiZhiDi": "神意之地",
        "LaNuoXiYa": "拉诺西亚",
        "HuanYingQunDao": "幻影群岛",
        "MengYaChi": "萌芽池",
        "YuZhouHeYin": "宇宙和音",
        "WoXianXiRan": "沃仙曦染",
        "ChenXiWangZuo": "晨曦王座",
        "BaiYinXiang": "白银乡",
        "BaiJinHuanXiang": "白金幻象",
        "ShenQuanHen": "神拳痕",
        "ChaoFengTing": "潮风亭",
        "LvRenZhanQiao": "旅人栈桥",
        "FuXiaoZhiJian": "拂晓之间",
        "Longchaoshendian": "龙巢神殿",
        "MengYuBaoJing": "梦羽宝境",
        "ZiShuiZhanQiao": "紫水栈桥",
        "YanXia": "延夏",
        "JingYuZhuangYuan": "静语庄园",
        "MoDuNa": "摩杜纳",
        "HaiMaoChaWu": "海猫茶屋",
        "RouFengHaiWan": "柔风海湾",
        "HuPoYuan": "琥珀原",
        "ShuiJingTa2": "水晶塔",
        "YinLeiHu2": "银泪湖",
        "TaiYangHaiAn2": "太阳海岸",
        "YiXiuJiaDe2": "伊修加德",
        "HongChaChuan2": "红茶川",
    }
    for (k, v) in world_dict.items():
        pattern = re.compile(k, re.IGNORECASE)
        world_name = pattern.sub(v, world_name)
    return world_name


# 获取物品id
def get_item_id(item_name, name_lang=""):
    url = "https://xivapi.com/search?indexes=Item&string=" + item_name
    if name_lang:
        url = url + "&language=" + name_lang
    if name_lang == "cn":
        url = (
            "https://cafemaker.wakingsands.com/search?indexes=Item&string=" + item_name
        )
    r = requests.get(url, timeout=60)
    j = r.json()
    if len(j["Results"]) > 0:
        result = max(j["Results"], key=lambda x: SequenceMatcher(None, x["Name"], item_name).ratio())
        return result["Name"], result["ID"]
    return "", -1


# 从 Universalis API 获取相应的交易数据，并将其格式化为文本消息返回给用户。如果未找到相应的物品或发生错误，则会返回相关错误信息。
def get_market_data(server_name, item_name, hq=False):
    new_item_name, item_id = get_item_id(item_name, "cn")
    if item_id < 0:
        item_name = item_name.replace("_", " ")
        name_lang = ""
        for lang in ["ja", "fr", "de"]:
            if item_name.endswith("|{}".format(lang)):
                item_name = item_name.replace("|{}".format(lang), "")
                name_lang = lang
                break
        new_item_name, item_id = get_item_id(item_name, name_lang)
        if item_id < 0:
            return '所查询物品"{}"不存在'.format(item_name)
    url = "https://universalis.app/api/{}/{}".format(server_name, item_id)
    print("market url:{}".format(url))
    r = requests.get(url, timeout=10)
    if r.status_code != 200:
        if r.status_code == 404:
            msg = "请确认所查询物品可交易且不可在NPC处购买"
        else:
            msg = "Error of HTTP request (code {}):\n{}".format(r.status_code, r.text)
        return msg
    j = r.json()
    msg = "{} 的 {}{} 数据如下：\n".format(server_name, new_item_name, "(HQ)" if hq else "")
    listing_cnt = 0
    for listing in j["listings"]:
        if hq and not listing["hq"]:
            continue
        retainer_name = listing["retainerName"]
        if "dcName" in j:
            retainer_name += "({})".format(localize_world_name(listing["worldName"]))
        msg += "{:,}x{} = {:,} {} {}\n".format(
            listing["pricePerUnit"],
            listing["quantity"],
            listing["total"],
            "HQ" if listing["hq"] else "  ",
            retainer_name,
        )
        listing_cnt += 1
        if listing_cnt >= 10:
            break
    TIMEFORMAT_YMDHMS = "%Y-%m-%d %H:%M:%S"
    last_upload_time = time.strftime(
        TIMEFORMAT_YMDHMS, time.localtime(j["lastUploadTime"] / 1000)
    )
    msg += "更新时间:{}".format(last_upload_time)
    if listing_cnt == 0:
        msg = "未查询到数据"
    return msg


# 简化物品名称
def handle_item_name_abbr(item_name):
    if item_name.startswith("第二期重建用的") and item_name.endswith("(检)"):
        item_name = item_name.replace("(", "（").replace(")", "）")
    if item_name.startswith("第二期重建用的") and not item_name.endswith("（检）"):
        item_name = item_name + "（检）"
    if item_name.upper() == "G12":
        item_name = "陈旧的缠尾蛟革地图"
    if item_name.upper() == "G11":
        item_name = "陈旧的绿飘龙革地图"
    if item_name.upper() == "G10":
        item_name = "陈旧的瞪羚革地图"
    if item_name.upper() == "G9":
        item_name = "陈旧的迦迦纳怪鸟革地图"
    if item_name.upper() == "G8":
        item_name = "陈旧的巨龙革地图图"
    if item_name.upper() == "G7":
        item_name = "陈旧的飞龙革地图"
    return item_name


# 错误处理；缩写处理；帮助
def handle_command(command_seg):
    if command_seg[0].lower() == "item":
        # if time.time() < user.last_api_time + user.api_interval:
        # print("current time:{}".format(time.time()))
        # print("last_api_time:{}".format(user.last_api_time))
        #if time.time() < user.last_api_time + 15:
        #    msg = "技能冷却中，请勿频繁调用".format(user.user_id)
        #    return msg
        server = None
        if len(command_seg) != 3:
            msg = "参数错误：\n/mitem $name $server: 查询$server服务器的$name物品交易数据"
            return msg
        server_name = command_seg[-1]
        if server_name in ("陆行鸟", "莫古力", "猫小胖", "豆豆柴"):
            pass
        elif server_name == "鸟":
            server_name = "陆行鸟"
        elif server_name == "猪":
            server_name = "莫古力"
        elif server_name == "猫":
            server_name = "猫小胖"
        elif server_name == "狗":
            server_name = "豆豆柴"
        else:
            pass
            # server = Server.objects.filter(name=server_name)
            # if not server.exists():
            #     msg = '找不到服务器"{}"'.format(server_name)
            #     return msg
        item_name = " ".join(command_seg[1:-1])
        hq = "hq" in item_name or "HQ" in item_name
        if hq:
            item_name = item_name.replace("hq", "", 1)
            item_name = item_name.replace("HQ", "", 1)
        item_name = handle_item_name_abbr(item_name)
        msg = get_market_data(server_name, item_name, hq)
        #user.last_api_time = time.time()
        #user.save(update_fields=["last_api_time"])
        return msg



