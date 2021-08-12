from typing import Tuple, Callable
import os
import time


# 配置项
device_serial = "emulator-5554"
resolution = (1280, 720) # 分辨率
default_tap_sleep = 2.0 # 默认点击后等待时间
default_dungeon_battle_time = 25 # 地下城战斗
default_battle_load_time = 12 # 默认进入战斗加载时间

# 32767来自adb shell getevent -p，参考https://raw.githubusercontent.com/vicety/Images/master/imagesScreenshot-2021-08-12-213010.png
rateW = resolution[0] / 32767
rateH = resolution[1] / 32767

# 类型定义
Loc = Tuple[str, str, str] # 位置, 位置, 说明

def to_int_tuple(hex_tuple:Loc):
    return (int(hex_tuple[0], 16), int(hex_tuple[1], 16))

PRESS_BUTTON_BACK = "input keyevent 4"

# 首级菜单
LOC_ADVANTURE = ("0000408e", "00007808", "冒险") # 来自getevent
LOC_GUILD_HOME = ("000050c5", "000076e8", "公会之家")
LOC_GACHA = ("00006470", "00007861", "扭蛋")
LOC_GUILD = ("00005c04", "00006806", "行会")
LOC_TASK = ("00006fc8", "000065af", "任务")
LOC_GIFT = ("000078bd", "00006712", "礼物")

# 次级（含以下）菜单
LOC_EXPLORE = ("00006226", "000020f8", "探索")
LOC_EXPLORE_EXP = ("00005093", "00003d2f", "经验本")
LOC_EXPLORE_MANA = ("0000709c", "000032cc", "Mana本")
LOC_EXPLORE_FIRST_QUEST = ("0000589b", "0000213b", "首个探索关卡")

LOC_HEART = ("00005c42", "00003e4f", "圣迹调查")
LOC_HEART2 = ("00005acc", "000025d1", "圣迹调查关卡2级")
LOC_HEART1 = ("000068d2", "0000391e", "圣迹调查关卡1级")

LOC_GACHA_FREE= ("000071a2", "00001071", "普通扭蛋")
LOC_GACHA_FREE_DO_GACHA = ("00005a81", "0000544a", "抽取普通扭蛋")

LOC_GUILD_MEMBER = ("00001aa1", "0000524d", "行会成员")
LOC_GUILD_LIKE = ("00006d40", "00002f83", "点赞第一名玩家")

LOC_DUNGEON = ("000075d2", "00002322", "地下城")

# 具体操作
LOC_REPEAT_MORE = ("000073ad", "00004e0f", "重复更多")
LOC_DO_REPEAT_BATTLE = ("00006470", "00005023", "使用n张") 
LOC_DO_MANUAL_BATTLE = ("00006b41", "00006a72", "手动挑战键")
LOC_CONFIRM = ("00004e94", "000057ed", "确认")

LOC_LATEST_DUNGEON = ("00006e78", "00003bf9", "最后一个地下城图")
LOC_DUNGEON_EX2_FIRST_ENEMY = ("00004d8e", "00004328", "地下城EX2敌人1")
LOC_DUNGEON_EX2_SECOND_ENEMY = ("0000566b", "000049d2", "地下城EX2敌人2")
LOC_DUNGEON_EX2_THIRD_ENEMY = ("00003fc7", "00004c97", "地下城EX2敌人3")
LOC_DUNGEON_EX2_FOURTH_ENEMY = ("000036ac", "0000474f", "地下城EX2敌人4")
LOC_DUNGEON_LEAVE = ("0000744f", "000064e8", "离开当前地下城")

LOC_TASK_COLLECT_ALL = ("000070f3", "0000690f", "收取所有任务奖励")

LOC_GUILD_COLLECT_ALL = ("0000780f", "000065f2", "公会之家收取体力")

LOC_GIFT_COLLECT_ALL = ("00006b8c", "00006ffc", "收取所有礼物")
LOC_GIFT_CONFIRM_COLLECT_ALL = ("00004cf9", "000070c3", "确认收取所有礼物")

LOC_MY_TEAM = ("00006ffa", "000015fb", "我的队伍")
LOC_FIRST_TEAM = ("00006663", "00002a3b", "第一个队伍")

LOC_SKIP = ("000079b7", "0000087b", "跳过")

# 战斗
LOC_AUTO = ("00007953", "000064e8", "自动")
LOC_SPEED_UP = ("0000793a", "000075b2", "")
LOC_BATTLE_RESULT_CHECK = ("000071e0", "00007319", "确认战斗结果")

# 其他
LOC_MEANINGLESS = ("00001d5b", "00001b00", "无意义位置") # 重复点击无意义位置，避免限定商店

def exec(cmd:str, sleep:float):
    ret = os.system("adb -s {} shell {}".format(device_serial, cmd))
    if ret != 0:
        print("failed executing {}, return {}".format(cmd, ret))
    time.sleep(sleep)

# 坐标计算参考了 https://blog.csdn.net/liu_zhen_wei/article/details/12559277
def press(location:Loc, sleep:float=default_tap_sleep):
    print("点击【{}】".format(location[2]))
    exec("input tap {} {}".format(int(int(location[0], 16) * rateW), int(int(location[1], 16) * rateH)), sleep=sleep)

def back():
    exec(PRESS_BUTTON_BACK, sleep=1)

# 进入界面，执行操作，退出
def context(loc:Callable[[Loc], None]):
    def decorator(f): # f:执行战斗函数
        def wrapper():
            print("进入【{}】".format(loc[2]))
            press(loc)
            f()
            print("退出【{}】".format(loc[2]))
            back()
        return wrapper
    return decorator

def start():
    # 从 dumpsys package com.bilibili.priconne 获得
    # 游戏启动
    exec("am start -n com.bilibili.priconne/com.bilibili.permission.PermissionActivity", sleep=15)
    # 登录
    press(LOC_MEANINGLESS, sleep=15)
    # 可能的新角色动画
    press(LOC_MEANINGLESS, sleep=3)
    # 每日签到
    press(LOC_SKIP, sleep=3)

    # 多次点击无意义位置尝试清理各种通知
    press(LOC_MEANINGLESS, sleep=1)
    press(LOC_MEANINGLESS, sleep=1)
    press(LOC_MEANINGLESS, sleep=1)

    back() # 退出通知界面

def exit():
    exec("am force-stop com.bilibili.priconne", sleep=2)

# 扫荡，之后退出关卡界面
def repeat_battle(battle_loc:Loc, n:int):
    press(battle_loc)

    for i in range(1, n):
        press(LOC_REPEAT_MORE, sleep=1.0)

    press(LOC_DO_REPEAT_BATTLE)
    press(LOC_CONFIRM)

    time.sleep(n * 2.0 + 1.0)

    press(LOC_MEANINGLESS)
    press(LOC_MEANINGLESS)
    back()

# 探索经验
@context(LOC_ADVANTURE)
@context(LOC_EXPLORE)
@context(LOC_EXPLORE_EXP)
def explore_exp():
    pass

# 探索mana
@context(LOC_ADVANTURE)
@context(LOC_EXPLORE)
@context(LOC_EXPLORE_MANA)
def explore_mana():
    repeat_battle(LOC_EXPLORE_FIRST_QUEST, 2)

# 心碎1
@context(LOC_ADVANTURE)
@context(LOC_HEART)
def heart1():
    repeat_battle(LOC_HEART1, 5)

# 心碎2
@context(LOC_ADVANTURE)
@context(LOC_HEART)
def heart2():
    repeat_battle(LOC_HEART2, 5)

# 公会之家体力收取
@context(LOC_GUILD_HOME)
def guild_collect_all():
    press(LOC_GUILD_COLLECT_ALL)
    press(LOC_MEANINGLESS)

# 免费十连
@context(LOC_GACHA)
def free_gacha():
    press(LOC_GACHA_FREE)
    press(LOC_GACHA_FREE_DO_GACHA)
    press(LOC_CONFIRM)
    time.sleep(3)
    back()

# 行会点赞
@context(LOC_GUILD)
@context(LOC_GUILD_MEMBER)
def guild_like():
    press(LOC_GUILD_LIKE)
    back()

# 地下城 毒瘴的暗棱 无boss
@context(LOC_ADVANTURE)
@context(LOC_DUNGEON)
def dungeon():
    # 选择地下城
    press(LOC_LATEST_DUNGEON)
    press(LOC_CONFIRM, sleep=5)

    press(LOC_DUNGEON_EX2_FIRST_ENEMY)
    press(LOC_DO_MANUAL_BATTLE)
    press(LOC_MY_TEAM)
    press(LOC_FIRST_TEAM)
    press(LOC_DO_MANUAL_BATTLE, sleep=default_battle_load_time) # 战斗开始

    # press(LOC_AUTO)
    # press(LOC_SPEED_UP)

    time.sleep(default_dungeon_battle_time)
    
    press(LOC_BATTLE_RESULT_CHECK, sleep=8)
    press(LOC_MEANINGLESS) # 确认地下城宝箱

    # 第2-4名敌人
    enemies = [LOC_DUNGEON_EX2_SECOND_ENEMY, LOC_DUNGEON_EX2_THIRD_ENEMY, LOC_DUNGEON_EX2_FOURTH_ENEMY]
    for enemy in enemies:
        press(enemy)
        press(LOC_DO_MANUAL_BATTLE)
        press(LOC_DO_MANUAL_BATTLE, sleep=default_battle_load_time)
        time.sleep(default_dungeon_battle_time)
        press(LOC_BATTLE_RESULT_CHECK, sleep=8)
        press(LOC_MEANINGLESS, sleep=5) # 确认地下城宝箱，等待角色走动

    press(LOC_DUNGEON_LEAVE)
    press(LOC_CONFIRM, sleep=5) # 确认离开地下城

# 收取每日任务奖励
@context(LOC_TASK)
def collect_daily_task_reward():
    press(LOC_TASK_COLLECT_ALL)
    press(LOC_MEANINGLESS)

# 收取所有礼物
@context(LOC_GIFT)
def collect_gift():
    press(LOC_GIFT_COLLECT_ALL)
    press(LOC_GIFT_CONFIRM_COLLECT_ALL)
    press(LOC_MEANINGLESS)

# 函数间无依赖，可任意修改顺序
collect_daily_task_reward()
free_gacha()
explore_exp()
explore_mana()
guild_collect_all()
collect_daily_task_reward()
collect_gift()

