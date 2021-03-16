import random
import time


class Pseudorandom:
    """基于当前数，n步长后的数一致的概率维持在0.3-0.5间"""
    def __init__(self, step=2, interval=1.8, trials=30):
        self.step = step  # N back中的步长N
        self.interval = interval  # 数字刷新间隔，单位为秒
        self.trials = trials  # 数字刷新次数
        self.dictate_count = 0  # 报数计数
        self.hit = 0  # 命中计数
        self.miss = 0  # 丢失计数
        self.mistake = 0  # 错误计数
        self.consistent = 0  # 一致计数
        self.current_num = None  # 当前显示数字
        self.current_seq = []  # 历史最新序列，序列长度等于步长step
        self.current_read = None  # 最近读数时间，用于反应时长计算
        self.current_click = None  # 最新点击时间，用于反应时长计算
        self.react_time = []  # 多次点击下的反应时长列表
        self.cal_allow = True  # 统计允许位，防止单个报数间隔内重复统计计数

    @staticmethod
    def partial_choice(partial_num):
        """伪随机选择，输入0-9的数，返回一个概率偏向partial_num的0-9随机数"""
        partial_prob = 0.3  # 偏向概率为0.3
        num_seq = list(range(10))
        if random.uniform(0, 1) > partial_prob:
            num_seq.remove(partial_num)  # 排除偏向数
            return random.choice(num_seq)
        else:
            return partial_num

    def dictate(self):
        """如果报数次数少于等于n，则产生0~9的随机数；若报数次数大于n，则产生伪随机数"""
        if self.dictate_count < self.step:
            # N步长内的数字完全随机
            number = random.randint(0, 9)
            self.current_seq.append(number)
        elif self.dictate_count == self.step:
            number = self.partial_choice(self.current_seq[0])
            self.current_seq.append(number)  # 当前数字入队保持更新但为保证队列长度不出队
        else:
            # N步长外的数字基于N步前数字偏向选择
            number = self.partial_choice(self.current_seq[1])
            self.current_seq.append(number)  # 当前数字入队保持更新
            self.current_seq.pop(0)  # 近期数字出队保持更新
        self.current_num = number  # 更新当前数字
        self.dictate_count += 1
        self.current_read = time.time()  # 读数完后刷新近期读数时间并允许点击统计
        self.cal_allow = True
        return number

    def check_hit_mistake(self):
        """按键时的命中和误操作检查"""
        # 这种检查必定在n步报数后进行
        self.current_click = time.time()
        duration = self.current_click - self.current_read
        # print('click：{} read：{} duration：{}'.format(self.current_click, self.current_read, duration))
        if self.cal_allow:
            """一个间隔时间内只允许统计一次hit或mistake数，间隔时间外的点击无效"""
            if self.current_seq[0] == self.current_seq[-1]:
                self.hit += 1
                self.react_time.append(duration)
            else:
                self.mistake += 1
        self.cal_allow = False  # 每次点击后将禁止统计直至下一次报数后允许，以防重复统计按键次数

    def consistent_cal(self):
        """一致数计算"""
        if self.current_seq[0] == self.current_seq[-1]:
            self.consistent += 1


# def dictate_test(p):
#     """如果前后一致频次逼近所设定概率，则认为dictate方法测试通过"""
#     ls = []
#     c = 0
#     epsilon = 0.1
#     for k in range(10000):
#         ls.append(p.dictate())
#     for j in range(p.step, 10000):
#         if ls[j-p.step] == ls[j]:
#             c += 1
#     expect = (p.prop_section[1] + p.prop_section[0]) / 2
#     if (c / 10000 - expect) < epsilon:
#         print('测试通过')
#     else:
#         print('测试未通过')
