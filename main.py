#########################################
#  Blackjack GUI Python   |             #
#########################################
import random
import sys
import os
import pygame
from input_box import InputBox


# Setting Up Pygame
pygame.init()
pygame.display.set_caption("Blackjack")

# CONSTANTS
SCREEN_DIMENSIONS = [800,600]
SCREEN_X = SCREEN_DIMENSIONS[0]
SCREEN_Y = SCREEN_DIMENSIONS[1]
CARD_DIMENSIONS = [90,130]
SCREEN =  pygame.display.set_mode(SCREEN_DIMENSIONS)
CARD_BACK_IMAGE = pygame.transform.scale(pygame.image.load(os.path.join("assets", "images" ,"back.png")),CARD_DIMENSIONS)
BG_IMG =  pygame.transform.scale(pygame.image.load(os.path.join("assets", "images" ,"background.jpg")),SCREEN_DIMENSIONS)
CLOCK  = pygame.time.Clock()




#Card Class which defines all class
class Card:
    def __init__(self, value, name , image ,pos , hide):
        self.value = value
        self.name = name
        self.image = image

        self.pos = pos
        self.hide = hide #reveal the card or not
        self.landed = False #check if card has finished it's landing animation or reached it's place

    def set_pos(self , new_pos):
        self.pos = new_pos

    def set_value(self , new_value):
        self.value = new_value

    def set_hide(self , new_hide):
        self.hide = new_hide

# Deck class
class Deck:
    def __init__(self):
        self.cards = []

    def create_deck(self):
        suits = ['diamonds', 'clubs', 'spades', 'hearts']
        royal_flush = ['king' , 'queen' , 'jack' , 'ace']
        for i in range(2, 11):
            for x in range(4):
                card_name = f'{i}_of_{suits[x]}'
                card_image = pygame.transform.scale(pygame.image.load(os.path.join("assets", "images" ,
                f"{card_name}.png")) ,CARD_DIMENSIONS )
                card = Card(i, card_name , card_image , [10,10] , True)
                self.cards.append(card)

        for i in range(4):
            for j in range(4):
                card_name = f'{royal_flush[j]}_of_{suits[i]}'
                card_image = pygame.transform.scale(pygame.image.load(os.path.join("assets", "images" ,
                f"{card_name}.png")) ,CARD_DIMENSIONS )
                card = Card(11 if royal_flush[j] == 'ace' else 10, card_name , card_image , [10,10] , True)
                self.cards.append(card)



        return self.cards

class GameStates:
    set_the_round = "set_the_round"
    place_your_bet = "place_your_bet"
    players_turn = "players_turn"
    dealers_turn = "dealers_turn"
    round_ends = "round_ends"


class PossibleOutcomes:
    won = "won"
    lost = "lost"
    tie = "tie"

# Game Class
class Game:
    def __init__(self):

        self.budget = 500
        self.currentBet = 0

        self.player = []
        self.dealer = []

        self.player_score = 0
        self.dealer_score = 0

        self.cards = []

        self.player_cards_revealed = False

        self.back_card_pos_incrementor = 3

        self.bet_input_box = InputBox(10, SCREEN_Y/2 -50, 100, 32 ,  pygame.font.Font(None, 32))
        self.middle_text = ""
        self.bottom_text = ""
        self.texts = []

        self.show_player_score = False
        self.show_dealer_score = False


        self.current_game_state = GameStates.set_the_round
        self.round_result = ""

        self.cards_landing = False
        self.disable_hittin_and_staying_input = True
        self.disable_reveal_cards_input = True


    def clearText(self):
        self.texts = []

    def reset(self):
        self.currentBet = 0
        self.player = []
        self.dealer = []
        self.player_score = 0
        self.dealer_score = 0
        self.cards = []

        self.player_cards_revealed = False

        self.current_game_state = GameStates.set_the_round

        self.round_result = ""

        self.show_player_score = False
        self.show_dealer_score = False

        self.disable_hittin_and_staying_input = True
        self.disable_reveal_cards_input = True


    def addText(self , string , x="" , y="" , color=pygame.Color("white") , background = None , size = 20 , center=False):
        FONT = pygame.font.Font(None, size)
        text = FONT.render(string , True , color , background)
        if center:
            text_rect = text.get_rect(center = SCREEN.get_rect().center)
            if x:
                text_rect.x = x
            elif y:
                text_rect.y =  y
            self.texts.append([ text , text_rect])
        else:
            self.texts.append([ text , [x,y]])

    def pass_cards(self, to=None, times=1):
        # pass cards to player and user
        for i in range(times):
            index = random.randint(0, len(self.cards) - 1)
            card = self.cards[index]

            if to == 'dealer':
                self.dealer.append(card)
                if card.name == "ace":
                    if self.dealer_score >= 11:
                        self.dealer_score += 1
                    else:
                        self.dealer_score += 11
                else:
                    self.dealer_score += card.value
            else:
                self.player.append(card)
                if card.name == "ace":
                    if self.player_score >= 11:
                        self.player_score += 1
                    else:
                        self.player_score += 11
                else:
                    self.player_score += card.value


            self.player_score = sum(list(map(lambda x: x.value, self.player)))
            self.cards.pop(index)


    def create_cards(self):
        deck = Deck()
        self.cards = deck.create_deck()
        random.shuffle(self.cards)
        self.player = []
        self.dealer = []
        self.player_score = 0
        self.dealer_score = 0

    def check_round_results(self):
        if self.round_result:
            self.middle_text = f"U {self.round_result} the bet"
        elif self.player_score > self.dealer_score:
            self.middle_text = 'U won the bet'
            self.round_result = PossibleOutcomes.won
        elif self.player_score < self.dealer_score:
            self.middle_text ='U Lost the bet'
            self.round_result = PossibleOutcomes.lost
        else:
            self.middle_text = 'tie'
            self.round_result = PossibleOutcomes.tie

        if self.round_result == PossibleOutcomes.won:
            self.budget += self.currentBet*2
        if self.round_result == PossibleOutcomes.tie:
            self.budget += self.currentBet

        self.bottom_text = "To play again , press enter"

    def hide_unhide_cards(self,cards , bool):
        for card in cards:
            card.hide = bool

    def draw_back_cards(self , cards , cards_of):
        for  index , card in enumerate(cards):
            if card.hide:
                SCREEN.blit(CARD_BACK_IMAGE ,card.pos)
            else:
                SCREEN.blit(card.image ,card.pos)

            if cards_of == "Player":
                if ( card.pos [1] < SCREEN_Y-CARD_DIMENSIONS[1]- (SCREEN_Y/16)):
                    card.pos [0] += (self.back_card_pos_incrementor * (index+1))
                    card.pos [1] += 10
                    card.landed = False
                    self.bet_input_box.set_active(False)

                    if self.cards_landing == False:
                        self.cards_landing = True

                elif card.landed == False:
                    card.landed = True
                    if self.current_game_state == GameStates.players_turn:
                        card.set_hide(False)
                    if self.cards_landing == True:
                        self.cards_landing = False
            elif cards_of == "Dealer":
                if ( card.pos [1] < CARD_DIMENSIONS[1] - (SCREEN_Y/7.6)):
                    card.pos [0] +=  (self.back_card_pos_incrementor * (index+1))
                    card.pos [1] += 1
                    card.landed = False
                    self.bet_input_box.set_active(False)
                    if self.cards_landing == False:
                        self.cards_landing = True

                elif card.landed == False:
                    card.landed = True
                    if self.current_game_state == GameStates.dealers_turn:
                        card.set_hide(False)
                    if self.cards_landing == True:
                        self.cards_landing = False


    def on_set_the_round(self):
        self.reset()
        if self.budget <= 0:
            sys.exit()

        self.create_cards()
        self.pass_cards(times=2)
        self.pass_cards('dealer', 2)
        self.bottom_text=""
        self.current_game_state = GameStates.place_your_bet

    def on_game_state_place_your_bet(self):
        self.middle_text = "Place Your Bet"
        self.bet_input_box.set_active(True)
        if self.bet_input_box.final_content:
            unchecked_bet = int(self.bet_input_box.final_content)
            if self.budget >= unchecked_bet:
                self.currentBet = unchecked_bet
                self.budget -= self.currentBet
                self.bet_input_box.set_final_content("")
                self.bet_input_box.set_active(False)
                self.bottom_text = ""
                self.current_game_state = GameStates.players_turn
            else:
                self.bottom_text = "Bet Can't be Bigger than budget"
                self.bet_input_box.set_final_content("")

    def on_game_state_players_turn(self):
        self.bet_input_box.set_active(False)
        self.show_player_score = True
        self.middle_text = ""
        if self.player_score > 21:
            self.round_result = PossibleOutcomes.lost
            self.current_game_state = GameStates.round_ends
            self.check_round_results()
            return

        self.dealer[0].hide = False

        if self.disable_reveal_cards_input == False:
            self.bottom_text = "Press r to reveal cards"
        else:
            self.bottom_text = ""

        if self.disable_hittin_and_staying_input == False:
            self.bottom_text = "Press Space To hit , Tab to stay"
        else:
            self.disable_reveal_cards_input = False

    def on_game_state_dealers_turn(self):
        self.bet_input_box.set_active(False)
        self.middle_text = ""
        self.bottom_text = ""
        self.show_dealer_score = True
        if self.dealer_score > 21:
            self.round_result = PossibleOutcomes.won
            self.current_game_state = GameStates.round_ends
            self.check_round_results()
            return

        dealer_mode = ['hit', 'stay', 'hit', 'stay', 'hit'][random.randint(0, 4)]

        if dealer_mode == 'hit':
            self.pass_cards('dealer', 1)
        else:
            self.current_game_state = GameStates.round_ends
            self.check_round_results()
            self.disable_hittin_and_staying_input = True
    def on_game_state_round_ends(self):
        self.bet_input_box.set_active(False)
        if self.cards_landing == False:
            self.hide_unhide_cards(self.player , False)
            self.hide_unhide_cards(self.dealer , False)
        self.disable_hittin_and_staying_input=True

    def blit_text(self):
        if self.cards_landing == False:
            self.addText(self.bottom_text ,center=True , y= SCREEN_Y-40-CARD_DIMENSIONS[1]-40 , size=30 , color=pygame.Color("white"))
            self.addText(self.middle_text ,center=True , size=60 , color=pygame.Color("white"))
            self.addText(f'Budget: {str(self.budget)}' , center=True , x = 10 , size=30 , color=pygame.Color("grey") )

            if self.show_player_score:
                if self.player_cards_revealed or self.current_game_state == GameStates.round_ends:
                    self.addText(str(self.player_score) , x=SCREEN_X-50 , y=SCREEN_Y-30-CARD_DIMENSIONS[1] , size=30 , color=pygame.Color("white"))
            if self.show_dealer_score:
                self.addText(str(self.dealer_score) ,x=SCREEN_X-50 , y= 30+CARD_DIMENSIONS[1] , size=30 , color=pygame.Color("white") )


        for text in self.texts:
            SCREEN.blit(text[0] , text[1])

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_running = False
                    pygame.quit()
                if event.type == pygame.KEYDOWN:
                    if self.disable_hittin_and_staying_input == False:
                        if self.cards_landing == False:
                            if event.key == pygame.K_SPACE:

                                self.pass_cards(times=1)
                            if event.key == pygame.K_TAB:
                                self.current_game_state = GameStates.dealers_turn
                                self.hide_unhide_cards(self.dealer , False)
                                self.current_game_state = GameStates.dealers_turn

                    if self.current_game_state == GameStates.round_ends:
                        if event.key == pygame.K_RETURN:
                            self.current_game_state = GameStates.set_the_round

                    if self.disable_reveal_cards_input == False:
                        if event.key == pygame.K_r:
                            self.hide_unhide_cards(self.player , False)
                            self.player_cards_revealed = True
                            self.disable_reveal_cards_input = True
                            self.disable_hittin_and_staying_input = False

                self.bet_input_box.handle_event(event)

            self.clearText()

            CLOCK.tick(30)
            SCREEN.blit(BG_IMG ,[0,0])
            SCREEN.blit(CARD_BACK_IMAGE ,(10 ,10))


            self.bet_input_box.update()
            self.bet_input_box.draw(SCREEN)

            if self.current_game_state == GameStates.set_the_round:
                self.on_set_the_round()

            elif self.current_game_state == GameStates.place_your_bet:
                self.on_game_state_place_your_bet()

            elif self.current_game_state == GameStates.players_turn:
                self.on_game_state_players_turn()

            elif self.current_game_state == GameStates.dealers_turn:
                self.on_game_state_dealers_turn()

            elif self.current_game_state == GameStates.round_ends:
                self.on_game_state_round_ends()


            Game.draw_back_cards(self.player , "Player")
            Game.draw_back_cards(self.dealer , "Dealer")

            self.blit_text()

            pygame.display.update()










Game = Game()
Game.run()


