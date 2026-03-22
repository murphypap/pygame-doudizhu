import pygame
import random
from collections import Counter

class CardAI:
    def __init__(self, name):
        self.name = name
        self.start_time = 0
        self.wait_time = 1000

    def play_card(self, hand, last_hand, turn_index, num_players):
        if self.start_time == 0:
            self.wait_time = random.randint(600, 1000)
            self.start_time = pygame.time.get_ticks()

        if pygame.time.get_ticks() - self.start_time >= self.wait_time:
            self.start_time = 0
            
            target_cards = []
            if last_hand is None:
                target_cards = self.plan_lead_play(hand)
            else:
                target_cards = self.find_bigger_cards(hand, last_hand)
            
            return turn_index, "play_cards", target_cards
        
        return turn_index, None, None

    def get_hand_stats(self, hand):
        hand_low_to_high = sorted(hand, key=lambda x: x.value)
        counts = Counter(c.value for c in hand_low_to_high)
        return hand_low_to_high, counts

    def plan_lead_play(self, hand):
        """
        聪明的主动出牌逻辑：
        策略：保护大牌，拒绝恶意拆牌，优先走掉中等大小的牌。
        """
        hand_low, counts = self.get_hand_stats(hand)
        
        # --- 策略核心：定义什么是不该拆的“关键张” ---
        # 炸弹(4张)和三张(3张)在前期是不建议拆开凑顺子的
        forbidden_to_split = [v for v in counts if counts[v] >= 3]

        # 1. 寻找顺子 (优化：不拆三张和炸弹，且不包含2)
        for length in range(12, 4, -1):
            for start_val in range(3, 16 - length):
                temp_straight = []
                can_use = True
                for i in range(length):
                    curr_v = start_val + i
                    # 如果这个顺子需要拆掉 3张 或 4张，且目前手牌还很多，就跳过
                    if curr_v in forbidden_to_split and len(hand) > 10:
                        can_use = False
                        break
                    if curr_v < 15 and counts[curr_v] >= 1:
                        card = [c for c in hand_low if c.value == curr_v][0]
                        temp_straight.append(card)
                    else:
                        can_use = False
                        break
                if can_use and len(temp_straight) == length:
                    return temp_straight

        # 2. 寻找连对 (同样遵循不拆原则)
        for length in range(10, 5, -2):
            for start_val in range(3, 16 - (length // 2)):
                temp_ds = []
                can_use = True
                for i in range(length // 2):
                    curr_v = start_val + i
                    if (curr_v in forbidden_to_split or counts[curr_v] < 2) and len(hand) > 10:
                        can_use = False
                        break
                    if curr_v < 15 and counts[curr_v] >= 2:
                        temp_ds.extend([c for c in hand_low if c.value == curr_v][:2])
                    else:
                        can_use = False
                        break
                if can_use and len(temp_ds) == length:
                    return temp_ds

        # 3. 三带二/一 (保护大牌：不主动出 222 或 AAA)
        for val in sorted(counts.keys()):
            # 如果手牌还多，不要主动打出 A(14) 或 2(15) 的三张
            if counts[val] == 3 and (val < 14 or len(hand) <= 5):
                main = [c for c in hand_low if c.value == val]
                rem_hand = [c for c in hand_low if c.value != val]
                rem_counts = Counter(c.value for c in rem_hand)
                
                # 优先带最小对子
                pairs = [v for v in sorted(rem_counts.keys()) if rem_counts[v] == 2]
                if pairs:
                    return main + [c for c in rem_hand if c.value == pairs[0]][:2]
                # 其次带最小单张
                if rem_hand:
                    return main + [rem_hand[0]]
                return main

        # 4. 四带二 (保护炸弹：只有当手牌不多时，才把炸弹当四带二打)
        if len(hand) < 10:
            for val in sorted(counts.keys()):
                if counts[val] == 4:
                    main = [c for c in hand_low if c.value == val]
                    rem_hand = [c for c in hand_low if c.value != val]
                    # 尝试带两对
                    rem_counts = Counter(c.value for c in rem_hand)
                    pairs = [v for v in sorted(rem_counts.keys()) if rem_counts[v] >= 2]
                    if len(pairs) >= 2:
                        pair_cards = []
                        for p_v in pairs[:2]: pair_cards.extend([c for c in rem_hand if c.value == p_v][:2])
                        return main + pair_cards
                    # 尝试带两单
                    if len(rem_hand) >= 2:
                        return main + rem_hand[:2]

        # 5. 最小对子 (保护 A 和 2)
        for val in sorted(counts.keys()):
            if counts[val] == 2 and (val < 14 or len(hand) <= 3):
                return [c for c in hand_low if c.value == val]

        # 6. 最小单张 (避开王和2)
        small_singles = [c for c in hand_low if counts[c.value] == 1 and c.value < 14]
        if small_singles:
            return [small_singles[0]]

        # 兜底：实在没办法了（手里全是 A 2 王），出最小的
        return [hand_low[0]]

    def find_bigger_cards(self, hand, last_hand):
        hand_low, counts = self.get_hand_stats(hand)
        t_type = last_hand["type"]
        t_val = last_hand["value"]
        t_len = last_hand["length"]

        # --- 聪明防守：如果对方牌多且出大牌，我不接 ---
        if t_val >= 14 and len(hand) > 10: # 对方出 A 或 2，我手牌还很多
            if random.random() > 0.2: return [] 

        def get_rem(current_hand, exclude_cards):
            return [x for x in current_hand if x not in exclude_cards]

        result = []

        # 基础搜索 (从小到大找最合适的压制，不浪费大牌)
        if t_type == "single":
            for card in hand_low:
                # 优化：如果我有比它大一点点的牌，就用那张，不用王直接拍死
                if card.value > t_val:
                    result = [card]
                    break
        elif t_type == "pair":
            for val in sorted(counts.keys()):
                if val > t_val and counts[val] >= 2:
                    result = [c for c in hand_low if c.value == val][:2]
                    break
        elif t_type == "triplet_2":
            for val in sorted(counts.keys()):
                if val > t_val and counts[val] >= 3:
                    main = [c for c in hand_low if c.value == val][:3]
                    rem = get_rem(hand_low, main)
                    rem_counts = Counter(c.value for c in rem)
                    pairs = [v for v in sorted(rem_counts.keys()) if rem_counts[v] >= 2]
                    if pairs:
                        result = main + [c for c in rem if c.value == pairs[0]][:2]
                        break
        # ... 其他牌型 (triplet_1, straight 等) 保持类似从小到大的逻辑
        elif t_type == "triplet_1":
            for val in sorted(counts.keys()):
                if val > t_val and counts[val] >= 3:
                    main = [c for c in hand_low if c.value == val][:3]
                    rem = get_rem(hand_low, main)
                    if rem:
                        result = main + [rem[0]]
                        break
        elif t_type == "straight":
            for val in sorted(counts.keys()):
                if val > t_val and val + t_len - 1 < 15:
                    temp = []
                    for i in range(t_len):
                        if counts[val+i] >= 1: temp.append([c for c in hand_low if c.value == val+i][0])
                        else: temp = []; break
                    if len(temp) == t_len:
                        result = temp; break

        # --- 绝地反击：对方快没牌了，不计代价扔炸弹 ---
        if not result and t_type != "bomb" and t_type != "rocket":
            # 这里的阈值很关键：如果对方剩 3 张或更少，我必须截断
            # 或者我自己快赢了，我也要交炸弹抢回出牌权
            if t_val > 10 or len(hand) < 6: # 简化逻辑：对方牌强或者我方牌少
                for val in sorted(counts.keys()):
                    if counts[val] == 4:
                        result = [c for c in hand_low if c.value == val]
                        break
        
        if t_type == "bomb" and not result:
            for val in sorted(counts.keys()):
                if val > t_val and counts[val] == 4:
                    result = [c for c in hand_low if c.value == val]
                    break

        # 火箭保护：不到万不得已不出火箭
        if not result and 16 in [c.value for c in hand] and 17 in [c.value for c in hand]:
            if t_type == "bomb" or len(hand) < 5:
                result = [c for c in hand if c.value in [16, 17]]

        return result

    def bid(self, hand):
        # 更加稳健的叫分：手里必须有硬通货（王或2）才叫
        if self.start_time == 0:
            self.start_time = pygame.time.get_ticks()
        if pygame.time.get_ticks() - self.start_time >= 1200:
            self.start_time = 0
            vals = [c.value for c in hand]
            score = vals.count(17)*4 + vals.count(16)*3 + vals.count(15)*2 + vals.count(14)*1
            # 只有在大牌分 > 6 且至少有一个王或两个2时才抢
            if score >= 7 and (17 in vals or 16 in vals or vals.count(15) >= 2):
                return "bid"
            return "nobid"
        return False