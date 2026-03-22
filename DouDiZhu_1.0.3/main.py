import pygame
import random
from card_ai import *
from collections import Counter
from os.path import join, dirname

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
CARD_WIDTH = 80
CARD_HEIGHT = 120
BASEPATH = dirname(__file__)

class Tip(pygame.sprite.Sprite):
    all_tips = []
    def __init__(self, type, group, pos=None, camp=None, font=None, text="", cards=None, index=0, color=(255, 255, 255)):
        super().__init__(group)
        self.type = type
        if self.type == "turn_prompt":
            self.image = pygame.Surface((30, 30))
            self.image.fill("gray")
            img = pygame.Surface((26, 26))
            img.fill("red")
            self.image.blit(img, (2, 2))
            self.rect = self.image.get_frect(center = pos)
            self.camp = camp
        if self.type == "tip":
            self.image = font.render(f"{text}", True, color)
            self.rect = self.image.get_frect()
            Tip.all_tips.insert(0, self)
            if len(Tip.all_tips) > 7:
                oldest_tip = Tip.all_tips.pop()
                oldest_tip.kill()
            self.pos = pygame.Vector2(21, 156)
            self.tar_pos = self.pos.copy()
        if self.type == "cards_num":
            self.image = pygame.Surface((30, 30)).convert_alpha()
            self.image.fill((150, 150, 150))
            self.font = font
            self.index = index
            num = self.font.render(f"{len(cards[self.index])}", True, "white")
            self.image.blit(num, (7, 7))
            self.rect = self.image.get_frect(center = pos)
        if self.type == "decoration":
            self.image = pygame.Surface((305, 150), pygame.SRCALPHA)
            pygame.draw.rect(self.image, (255, 255, 255, 100), (0, 0, 305, 150), border_radius=10)
            self.rect = self.image.get_frect(topleft = pos)
        if self.type == "decoration_2":
            self.image = pygame.Surface((1000, 700), pygame.SRCALPHA)
            self.image.fill((255, 255, 255, 100))
            self.rect = self.image.get_frect(topleft = pos)
        if self.type == "ll":
            self.image = pygame.image.load(join(BASEPATH, "landlord.png")).convert()
            self.image = pygame.transform.scale(self.image, (30, 30))
            self.rect = self.image.get_frect(center = pos)

    def update(self, turn, cards):
        if self.type == "turn_prompt":
            self.image.fill("gray")
            if turn == self.camp:
                img = pygame.Surface((26, 26))
                img.fill("green")
                self.image.blit(img, (2, 2))
            else:
                img = pygame.Surface((26, 26))
                img.fill("red")
                self.image.blit(img, (2, 2))

        if self.type == "tip":
            if self in Tip.all_tips:
                offset = Tip.all_tips.index(self)
                self.tar_pos.y = 146 - offset * 20
                self.pos += (self.tar_pos - self.pos) * 0.1
                self.rect.topleft = self.pos

        if self.type == "cards_num":
            self.image.fill((150, 150, 150))
            num = self.font.render(f"{len(cards[self.index])}", True, "white")
            self.image.blit(num, (7, 7))

class Card(pygame.sprite.Sprite):
    def __init__(self, suit, rank, value, font, group, suits, pos=(460, 290)):
        super().__init__(group)
        self.suit = suit   # 花色
        self.rank = rank   # 文字标识 (2, 3... J, Q, K, A, Small King)
        self.value = value # 用于比较大小的权重值
        self.selected = False
        self.selectable = True
        self.get_img(font, suits)

        self.pos = pygame.Vector2(pos)
        self.tar_pos = pygame.Vector2(pos)
        self.rect = self.img.get_frect(topleft = self.pos)

    def update(self):
        if self.pos.distance_to(self.tar_pos) < 25:
            offset = 0.2
        else:
            offset = 0.12

        self.pos += (self.tar_pos - self.pos) * offset
        self.rect.topleft = self.pos
    
    def get_img(self, font, suits):
        self.img = pygame.Surface((CARD_WIDTH, CARD_HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(self.img, (0, 0, 0), (0, 0, CARD_WIDTH, CARD_HEIGHT), border_radius=5)
        pygame.draw.rect(self.img, (245, 245, 245), (2, 2, CARD_WIDTH-4, CARD_HEIGHT-4), border_radius=5)
        img = suits.get(self.suit).copy()
        if not isinstance(img, list):
            wm = pygame.Surface(img.get_size()).convert_alpha()
            wm.fill((25, 25, 25))
            img.blit(wm, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
            self.img.blit(img, (CARD_WIDTH / 2 - img.get_width() / 2, CARD_HEIGHT / 2 - img.get_height() / 2))
        if self.value < 16:
            self.img.blit(font.render(f"{self.rank}" , True, "black"), (6, 6))
        else:
            self.img.blit(font.render(f"{self.rank.split()[0]}" , True, "black"), (6, 6))
            self.img.blit(font.render(f"{self.rank.split()[1]}" , True, "black"), (6, 24))

    def fold(self):
        self.img.fill((50, 50, 50), special_flags=pygame.BLEND_SUB)

class Button(pygame.sprite.Sprite):
    def __init__(self, text, group, pos=(400, 505), font_size=30, offset=(15, 5)):
        super().__init__(group)
        self.font = pygame.font.Font(None, font_size)
        self.text = text
        self.offset = offset
        self.img = pygame.surface.Surface((75, 30)).convert_alpha()
        self.img.fill((100, 100, 100))
        self.img.blit(self.font.render(self.text, True, (255, 255, 255)), self.offset)
        self.rect = self.img.get_rect(center=pos)

        self.id = text.lower()

    def update(self, mouse_pos, mouse_pre, mouse_jpre, turn, select, state):
        if turn == "player":
            if self.rect.collidepoint(mouse_pos):
                self.img.fill((180, 180, 180))
                self.img.blit(self.font.render(self.text, True, (255, 255, 255)), self.offset)
                if mouse_jpre[0]:
                    if self.id == "play" and state == "game":
                        if game.engine.selected_cards:
                            if game.engine.check_valid():
                                game.engine.play_cards(game.engine.player_hand)
                                game.engine.turn_index += 1
                                game.engine.turn_index %= len(game.engine.turns)
                                # print(f"玩家选择出牌")
                            else:
                                Tip("tip", game.engine.all_tips, font=game.engine.font2, text="Invalid hand or hand is too low!")
                        else:
                            Tip("tip", game.engine.all_tips, font=game.engine.font2, text="Please select the cards you want to play!")
                    elif self.id == "skip":
                        if state == "bid":
                            game.engine.player_passed_bid = True
                        elif state == "game":
                            if game.engine.last_hand is None:
                                Tip("tip", game.engine.all_tips, font=game.engine.font2, text="You must play cards!", color=(255, 100, 0))
                            elif game.engine.skip_count < 2:
                                game.engine.turn_index = (game.engine.turn_index + 1) % len(game.engine.turns)
                                game.engine.skip_count += 1
                                if game.engine.skip_count >= 2:
                                    game.engine.last_hand = None

                                for card in game.engine.player_hand:
                                    card.selected = False
                                game.engine.move_cards(game.engine.player_hand)
                                game.engine.selected_cards.clear()
                                Tip("tip", game.engine.all_tips, font=game.engine.font2, text="You pass")
                        else:
                            Tip("tip", game.engine.all_tips, font=game.engine.font2, text="You can't skip!", color=(255, 100, 0))
            else:
                self.img.fill((150, 150, 150))
                self.img.blit(self.font.render(self.text, True, (255, 255, 255)), self.offset)
        else:
            self.img.fill((80, 80, 80))
            self.img.blit(self.font.render(self.text, True, (200, 200, 200)), self.offset)

        if state == "end_game":
            if self.id == "restart":
                if self.rect.collidepoint(mouse_pos):
                    self.img.fill((180, 180, 180))
                    self.img.blit(self.font.render(self.text, True, (255, 255, 255)), self.offset)
                    if mouse_jpre[0]:
                        game.engine.state_index = len(game.engine.states) - 1
                else:
                    self.img.fill((150, 150, 150))
                    self.img.blit(self.font.render(self.text, True, (255, 255, 255)), self.offset)

class Engine:
    def __init__(self):
        self.initialize()

    def _create_deck(self, font):
        suits = ['♠', '♥', '♣', '♦']
        ranks = {'3':3, '4':4, '5':5, '6':6, '7':7, '8':8, '9':9, '10':10, 
                 'J':11, 'Q':12, 'K':13, 'A':14, '2':15}
        deck = [Card(s, r, v, font, self.all_cards, self.suits) for s in suits for r, v in ranks.items()]
        deck.append(Card('SJ', 'Small Joker', 16, font, self.all_cards, self.suits))
        deck.append(Card('BJ', 'Big Joker', 17, font, self.all_cards, self.suits))
        random.shuffle(deck)
        return deck

    def deal_cards(self):
        self.player_hand = sorted(self.deck[:17], key=lambda x: x.value, reverse=True)
        self.ai_left_hand = sorted(self.deck[17:34], key=lambda x: x.value, reverse=True)
        self.ai_right_hand = sorted(self.deck[34:51], key=lambda x: x.value, reverse=True)
        self.landlord_cards = self.deck[51:]
        for i, card in enumerate(self.landlord_cards):
            card.tar_pos = pygame.Vector2((450 + (i - 1) * 120, 20))

        self.organize_cards()
        self.set_initial_turn()

    def set_initial_turn(self):
        Tip("tip", self.all_tips, font=self.font2, text="---------- Bidding for the Landlord ----------", color=(232, 113, 18))
        search_ranks = ['3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A', '2']
        target_suit = '♥'

        hands = {
            0: [self.player_hand, "You have", "You choose"],    # "player"
            1: [self.ai_left_hand, "Left player has", "Left player chooses"],   # "ai_left"
            2: [self.ai_right_hand, "Right player has", "Right player chooses"]   # "ai_right"
        }

        for rank in search_ranks:
            for index, hand in hands.items():
                for card in hand[0]:
                    if card.suit == target_suit and card.rank == rank:
                        self.turn_index = index
                        self.landlord_candidate = index
                        Tip("tip", self.all_tips, font=self.font2, text=f"{hand[1]} {card.rank} of heart", color=(255, 232, 130))
                        Tip("tip", self.all_tips, font=self.font2, text=f"{hand[2]} first", color=(255, 232, 130))
                        return

        self.turn_index = 0

    def initialize(self):
        Tip.all_tips.clear()
        self.__dict__.clear()
        self.font = pygame.font.Font(None, 24)
        self.font2 = pygame.font.Font(None, 21)

        self.player_pos = 550
        self.player_select_offset = 20
        self.show_landlord_time = 1000
        self.turns = ["player", "ai_left", "ai_right"]
        self.states = ["bid", "show_landlord", "game", "end_game", "restart"]
        self.texts = {"player": "It's the left player's turn", 
                      "ai_left": "It's the right player's turn", 
                      "ai_right": "It's your turn", }

        self.card_ai_left = CardAI("AI Left")
        self.card_ai_right = CardAI("AI Right")
        #--------------------------------------------------
        self.all_cards = pygame.sprite.Group()
        self.all_buttons = pygame.sprite.Group()
        self.all_tips = pygame.sprite.Group()

        self.suits = {
        '♠': pygame.image.load(join(BASEPATH, "spade.png")).convert_alpha(), 
        '♥': pygame.image.load(join(BASEPATH, "heart.png")).convert_alpha(), 
        '♣': pygame.image.load(join(BASEPATH, "club.png")).convert_alpha(), 
        '♦': pygame.image.load(join(BASEPATH, "diamond.png")).convert_alpha(), 
        'SJ': [], 
        'BJ': []
        }

        self.deck = self._create_deck(self.font)
        self.player_hand = []
        self.ai_left_hand = []
        self.ai_right_hand = []
        self.landlord_cards = []

        Tip("decoration", self.all_tips, pos=(12, 15))
        self.deal_cards()

        self.turn = self.turns[self.turn_index]
        self.last_turn = None
        self.state_index = 0
        self.state = self.states[self.state_index]
        self.played_cards = []
        self.selected_cards = []
        self.played = []
        self.back_card()
        self.bid_time = 0
        self.show_landlord = True
        self.player_select = False
        self.last_hand = None
        self.skip_count = 0
        self.player_passed_bid = False

        self.player_play_button = Button("Play", self.all_buttons, pos=(425, 505))
        self.player_skip_button = Button("skip", self.all_buttons, pos=(525, 505))
        self.player_bid_button = Button("Bid", self.all_buttons, pos=(425, 505), offset=(20, 5))
        self.player_turn_prompt = Tip("turn_prompt", self.all_tips, pos=(340, 505), camp="player")
        self.ai_left_turn_prompt = Tip("turn_prompt", self.all_tips, pos=(150, 200), camp="ai_left")
        self.ai_right_turn_prompt = Tip("turn_prompt", self.all_tips, pos=(845, 200), camp="ai_right")
        Tip("cards_num", self.all_tips, font=self.font, pos=(280, 505), cards=[self.player_hand, self.ai_left_hand, self.ai_right_hand], index=0)
        Tip("cards_num", self.all_tips, font=self.font, pos=(150, 250), cards=[self.player_hand, self.ai_left_hand, self.ai_right_hand], index=1)
        Tip("cards_num", self.all_tips, font=self.font, pos=(845, 250), cards=[self.player_hand, self.ai_left_hand, self.ai_right_hand], index=2)

    def update(self, keys, keys_j, mouse_pos, mouse_pre, mouse_jpre):
        if self.state == self.states[len(self.states) - 1]:
            self.initialize()
            return

        self.turn = self.turns[self.turn_index]
        self.state = self.states[self.state_index]
        self.all_cards.update()
        self.all_buttons.update(mouse_pos, mouse_pre, mouse_jpre, self.turn, self.selected_cards, self.state)
        self.all_tips.update(self.turn, [self.player_hand, self.ai_left_hand, self.ai_right_hand])
        
        if self.state == "game":
            if self.check_vic():
                Tip("decoration_2", self.all_tips, pos=(0, 0))
                self.restart = Button("restart", self.all_buttons, pos=(500, 350), offset=(5, 5))
                self.state_index += 1
                self.state_index %= len(self.states)

            if self.turn == "player":
                if mouse_jpre[0]:
                    self.selectable = self.calculate_boud(self.player_hand, pygame.Vector2(mouse_pos))
                    self.spread_cards(self.player_hand)
                if mouse_pre[0]:
                    if self.selectable:
                        for card in reversed(self.player_hand):
                            if card.rect.collidepoint(mouse_pos):
                                if card.selectable:
                                    if card.selected:
                                        card.selected = False
                                        self.selected_cards.remove(card)
                                    else:
                                        card.selected = True
                                        self.selected_cards.append(card)
                                    self.move_card(card)
                                    card.selectable = False
                                break
                else:
                    self.selectable = False
                    for card in self.player_hand:
                        card.selectable = True

            elif self.turn == "ai_left":
                _, func, cards = self.card_ai_left.play_card(self.ai_left_hand, self.last_hand, self.turn_index, len(self.turns))
                if func == "play_cards":
                    self.selected_cards = cards
                    if not self.selected_cards:
                        self.skip_count += 1
                        if self.skip_count >= 2: self.last_hand = None
                        Tip("tip", self.all_tips, font=self.font2, text="Left player passes")
                        self.turn_index = (self.turn_index + 1) % 3
                    elif self.check_valid():
                        self.play_cards(self.ai_left_hand)
                        self.skip_count = 0
                        self.turn_index = (self.turn_index + 1) % len(self.turns)
                    else:
                        self.selected_cards.clear()
                        self.skip_count += 1
                        if self.skip_count >= 2: self.last_hand = None
                        Tip("tip", self.all_tips, font=self.font2, text="AI pass")
                        self.turn_index = (self.turn_index + 1) % len(self.turns)

            elif self.turn == "ai_right":
                # _, func, cards = self.card_ai_right.play_card(self.ai_right_hand, self.played_cards, self.landlord, self.turn_index, len(self.turns))
                _, func, cards = self.card_ai_right.play_card(self.ai_right_hand, self.last_hand, self.turn_index, len(self.turns))
                if func == "play_cards":
                    self.selected_cards = cards
                    if not self.selected_cards:
                        self.skip_count += 1
                        if self.skip_count >= 2: self.last_hand = None
                        Tip("tip", self.all_tips, font=self.font2, text="Right player passes")
                        self.turn_index = (self.turn_index + 1) % 3
                    elif self.check_valid():
                        self.play_cards(self.ai_right_hand)
                        self.skip_count = 0
                        self.turn_index = (self.turn_index + 1) % len(self.turns)
                    else:
                        self.selected_cards.clear()
                        self.skip_count += 1
                        if self.skip_count >= 2: self.last_hand = None
                        Tip("tip", self.all_tips, font=self.font2, text="AI pass")
                        self.turn_index = (self.turn_index + 1) % len(self.turns)

        if self.state == "bid":
            if self.bid_time >= len(self.turns):
                self.landlord = self.turns[self.landlord_candidate]
                self.turn_index = self.landlord_candidate
                self.state_index = self.states.index("show_landlord")

            if self.turn == "player":
                if mouse_jpre[0]:
                    if self.player_bid_button.rect.collidepoint(mouse_pos):
                        self.landlord = "player"
                        self.state_index += 1
                        self.state_index %= len(self.states)
                    if self.player_skip_button.rect.collidepoint(mouse_pos):
                        self.player_passed_bid = False
                        self.bid_time += 1
                        self.turn_index = (self.turn_index + 1) % len(self.turns) # 只有这里切换到 AI
                        Tip("tip", self.all_tips, font=self.font2, text="You choose not to bid", color=(255, 255, 255))

            if self.turn == "ai_left":
                result = self.card_ai_left.bid(self.ai_left_hand)
                if result:
                    if result == "bid":
                        self.landlord = "ai_left"
                        self.state_index += 1
                        self.state_index %= len(self.states)

                    elif result == "nobid":
                        self.turn_index += 1
                        self.turn_index %= len(self.turns)
                        self.bid_time += 1
                        Tip("tip", self.all_tips, font=self.font2, text="The left player chooses not to bid", color=(255, 232, 130))

            if self.turn == "ai_right":
                result = self.card_ai_right.bid(self.ai_right_hand)
                if result:
                    if result == "bid":
                        self.landlord = "ai_right"
                        self.state_index += 1
                        self.state_index %= len(self.states)

                    elif result == "nobid":
                        self.turn_index += 1
                        self.turn_index %= len(self.turns)
                        self.bid_time += 1
                        Tip("tip", self.all_tips, font=self.font2, text="The right player chooses not to bid", color=(255, 232, 130))

        if self.state == "show_landlord":
            if self.show_landlord:
                self.start_time = pygame.time.get_ticks()
                self.show_landlord = False
                if self.landlord == "player":
                    Tip("tip", self.all_tips, font=self.font2, text="------------- You are the Landlord -------------", color=(232, 113, 18))
                elif self.landlord == "ai_left":
                    Tip("tip", self.all_tips, font=self.font2, text="- The player on the left is the Landlord -", color=(232, 113, 18))
                elif self.landlord == "ai_right":
                    Tip("tip", self.all_tips, font=self.font2, text="- The player on the right is the Landlord -", color=(232, 113, 18))

            else:
                if pygame.time.get_ticks() - self.start_time >= self.show_landlord_time:
                    self.state_index += 1
                    self.state_index %= len(self.states)
                    self.choose_landlord()

    def draw(self, surf):
        surf.fill((34, 139, 34))
        surf.blit(self.player_skip_button.img, self.player_skip_button.rect)
        self.all_tips.draw(surf)
        surf.blit(self.player_play_button.img, self.player_play_button.rect)

        for card in self.player_hand:
            surf.blit(card.img, card.rect)
        for card in self.ai_left_hand:
            surf.blit(self.card_back_img, card.rect)
        for card in self.ai_right_hand:
            surf.blit(self.card_back_img, card.rect)
        for card in self.played_cards:
            surf.blit(card.img, card.rect)

        if self.state == "bid":
            surf.blit(self.player_bid_button.img, self.player_bid_button.rect)
        
            for card in self.landlord_cards:
                surf.blit(self.card_back_img, card.rect)

        if self.state == "show_landlord":
            surf.blit(self.player_bid_button.img, self.player_bid_button.rect)

            for card in self.landlord_cards:
                surf.blit(card.img, card.rect)

        if self.state == "end_game":
            surf.blit(self.restart.img, self.restart.rect)

    def organize_cards(self):
        for i, card in enumerate(reversed(self.player_hand)):
            card.tar_pos = pygame.Vector2(500 + ((len(self.player_hand) / 2) - i - 2 ) * 35, self.player_pos)
        for i, card in enumerate(reversed(self.ai_left_hand)):
            card.tar_pos = pygame.Vector2(30, 300 + ((len(self.ai_left_hand) / 2) - i - 2 ) * 12)
        for i, card in enumerate(reversed(self.ai_right_hand)):
            card.tar_pos = pygame.Vector2(890, 300 + ((len(self.ai_right_hand) / 2) - i - 2 ) * 12)

    def choose_landlord(self):
        if self.landlord == 'player':
            self.player_hand += self.landlord_cards
            self.player_hand.sort(key=lambda x: x.value, reverse=True)
            self.turn_index = 0
            Tip("tip", self.all_tips, font=self.font2, text="It's your turn", color=(255, 232, 130))
            Tip("ll", self.all_tips, pos=(220, 505))
        elif self.landlord == 'ai_left':
            self.ai_left_hand += self.landlord_cards
            self.ai_left_hand.sort(key=lambda x: x.value, reverse=True)
            self.turn_index = 1
            Tip("tip", self.all_tips, font=self.font2, text="It's the left player's turn", color=(255, 232, 130))
            Tip("ll", self.all_tips, pos=(150, 300))
        else:
            self.ai_right_hand += self.landlord_cards
            self.ai_right_hand.sort(key=lambda x: x.value, reverse=True)
            self.turn_index = 2
            Tip("tip", self.all_tips, font=self.font2, text="It's the right player's turn", color=(255, 232, 130))
            Tip("ll", self.all_tips, pos=(845, 300))
        
        self.last_hand = None      # 确保地主是第一手出牌
        self.skip_count = 0        # 清空之前的跳过计数
        self.played_cards.clear()  # 清空场上的牌
        self.played.clear()        # 清空上一次记录
        self.selected_cards.clear()
        self.organize_cards()

    def move_card(self, card):
        """adjust player's card"""
        card.tar_pos.y = self.player_pos - self.player_select_offset if card.selected else self.player_pos

    def move_cards(self, cards):
        """adjust player's cards"""
        for card in cards:
            card.tar_pos.y = self.player_pos - self.player_select_offset if card.selected else self.player_pos

    def play_cards(self, player):
        """move the discarded cards to the center, and organize the player's hand"""
        if self.selected_cards:
            Tip("tip", self.all_tips, font=self.font2, text=self.texts.get(self.turn), color=(255, 232, 130))
            if self.played:
                for card in self.played:
                    card.fold()

            current_play = self.selected_cards.copy()
            for card in current_play:
                player.remove(card)

            current_play = self.sorting_cards(current_play)

            for i, card in enumerate(current_play):
                card.tar_pos = pygame.Vector2(500 + (i - (len(self.selected_cards) / 2) - 1) * 30, 300)
            
            self.played = current_play
            played = []
            for card in self.played:
                played.append(card.rank)

            self.last_hand = self.temp_analysis
            self.skip_count = 0
            self.played_cards.extend(current_play)
            self.selected_cards.clear()
            self.organize_cards()
        else:
            Tip("tip", self.all_tips, font=self.font2, text="The player chooses not to play a card", color=(255, 255, 255))
            Tip("tip", self.all_tips, font=self.font2, text=self.texts.get(self.turn), color=(255, 225, 20))


    def sorting_cards(self, cards):
        if not cards:
            return []

        counts = Counter(card.value for card in cards)
        sorted_cards = sorted(cards, key=lambda c: (-counts[c.value], -c.value))
        return sorted_cards

    def back_card(self):
        self.card_back_img = pygame.Surface((CARD_WIDTH, CARD_HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(self.card_back_img, (0, 0, 0), (0, 0, CARD_WIDTH, CARD_HEIGHT), border_radius=5)
        pygame.draw.rect(self.card_back_img, (250, 250, 250), (2, 2, CARD_WIDTH-4, CARD_HEIGHT-4), border_radius=5)

    def spread_cards(self, cards):
        pass

    def calculate_boud(self, cards, mouse_pos):
        for card in cards:
            if card.rect.collidepoint(mouse_pos):
                return True
        return False

    def check_valid(self):
        current_analysis = self.analyze_hand(self.selected_cards)
        if not current_analysis:
            return False

        if not self.last_hand:
            self.temp_analysis = current_analysis
            return True

        if current_analysis["type"] == "rocket":
            self.temp_analysis = current_analysis
            return True
        
        if self.last_hand["type"] != "bomb" and self.last_hand["type"] != "rocket" and current_analysis["type"] == "bomb":
            self.temp_analysis = current_analysis
            return True
        
        if current_analysis["type"] == self.last_hand["type"] and \
            current_analysis["length"] == self.last_hand["length"] and \
            current_analysis["value"] > self.last_hand["value"]:
                self.temp_analysis = current_analysis
                return True

        return False
    
    def analyze_hand(self, cards):
        if not cards: return None
        n = len(cards)
        values = sorted([c.value for c in cards])
        counts = Counter(values)
        # 按张数从多到少排序，张数相同按值从大到小
        count_values = sorted(counts.items(), key=lambda x: (-x[1], -x[0]))
        
        # 1. 特殊牌型：火箭 (Small Joker + Big Joker)
        if n == 2 and values[0] == 16 and values[1] == 17:
            return {"type": "rocket", "value": 999, "length": 2}
        
        # 2. 基础牌型：单张和对子
        if n == 1:
            return {"type": "single", "value": values[0], "length": 1}
        if n == 2 and values[0] == values[1]:
            return {"type": "pair", "value": values[0], "length": 2}

        # 3. 四张核心牌型 (炸弹、四带二)
        if count_values[0][1] == 4:
            four_val = count_values[0][0]
            if n == 4: # 纯炸弹
                return {"type": "bomb", "value": four_val, "length": 4}
            if n == 6: # 四带二单 (可以是两张不同的单牌)
                return {"type": "four_with_two", "value": four_val, "length": 6}
            if n == 8: # 四带二对
                # 剩下的牌必须全是对子 (例如 4个J + 两个3 + 两个4)
                rem_counts = [v[1] for v in count_values[1:]]
                if all(c >= 2 for c in rem_counts):
                    return {"type": "four_with_two_pairs", "value": four_val, "length": 8}

        # 4. 三张核心牌型 (三不带、三带一、三带二)
        if count_values[0][1] == 3:
            three_val = count_values[0][0]
            if n == 3: # 三不带
                return {"type": "triplet", "value": three_val, "length": 3}
            if n == 4: # 三带一
                return {"type": "triplet_1", "value": three_val, "length": 4}
            if n == 5: # 三带二 (带一个对子)
                if count_values[1][1] >= 2:
                    return {"type": "triplet_2", "value": three_val, "length": 5}

        # 5. 顺子 (不包含 2 或 王)
        if n >= 5 and max(values) < 15 and len(counts) == n:
            if values[-1] - values[0] == n - 1:
                return {"type": "straight", "value": values[0], "length": n}

        # 6. 连对 (不包含 2 或 王)
        if n >= 6 and n % 2 == 0 and max(values) < 15:
            is_ds = True
            for i in range(0, n, 2):
                if values[i] != values[i+1] or (i > 0 and values[i] != values[i-1] + 1):
                    is_ds = False
                    break
            if is_ds:
                return {"type": "double_straight", "value": values[0], "length": n}

        # 7. 飞机逻辑 (连三)
        triplets = sorted([v for v, c in counts.items() if c >= 3 and v < 15])
        if len(triplets) >= 2:
            # 找到最长连续三头
            max_chain = []
            current_chain = [triplets[0]]
            for i in range(1, len(triplets)):
                if triplets[i] == triplets[i-1] + 1:
                    current_chain.append(triplets[i])
                else:
                    if len(current_chain) > len(max_chain): max_chain = current_chain
                    current_chain = [triplets[i]]
            if len(current_chain) > len(max_chain): max_chain = current_chain
            
            chain_len = len(max_chain)
            if chain_len > 2:
                return None

            if chain_len >= 2:
                base_val = max_chain[0]
                if n == chain_len * 3: # 飞机不带
                    return {"type": "airplane", "value": base_val, "length": chain_len}
                if n == chain_len * 4: # 飞机带单
                    return {"type": "airplane_wings", "value": base_val, "length": chain_len}
                if n == chain_len * 5: # 飞机带对
                    rem_cards = [v for v, c in counts.items() if v not in max_chain]
                    if all(counts[v] >= 2 for v in rem_cards):
                        return {"type": "airplane_pair", "value": base_val, "length": chain_len}

        return None

    def check_vic(self):
        if len(self.player_hand) == 0 or len(self.ai_left_hand) == 0 or len(self.ai_right_hand) == 0:
            return True
        return False

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("斗地主")
        self.clock = pygame.time.Clock()
        self.engine = Engine()

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(60) / 1000

            events = pygame.event.get()
            keys = pygame.key.get_pressed()
            keys_j = pygame.key.get_just_pressed()
            mouse_pos = pygame.mouse.get_pos()
            mouse_pre = pygame.mouse.get_pressed()
            mouse_jpre = pygame.mouse.get_just_pressed()

            for event in events:
                if event.type == pygame.QUIT:
                    running = False

            self.engine.update(keys, keys_j, mouse_pos, mouse_pre, mouse_jpre)
            self.engine.draw(self.screen)

            pygame.display.flip()

        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()