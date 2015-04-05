#!/usr/bin/env python
# -*- coding: utf-8 -*-

import itertools
import random
import Tkinter as tk
from PIL import *
from genetic import *

class Card:
	# clubs, diamonds, hearts, spades
	SUITS = 'cdhs'
	RANKS = '23456789TJQKA'
	# 0: one-eyed, 1:two-eyed
	DECKS = '01'

	# Special cards
	REMOVERS = [''.join(card) for card in itertools.product("J", SUITS, "0")]
	JOKERS = [''.join(card) for card in itertools.product("J", SUITS, "1")]

	def __init__(self, rank, suit, deck):
		if not(suit in Card.SUITS):
			raise Exception("Invalid suit")
		if not(rank in Card.RANKS):
			raise Exception("Invalid rank")
		if not(deck in Card.DECKS):
			raise Exception("Invalid deck")
		self.suit = suit
		self.rank = rank
		self.deck = int(deck)

	@classmethod
	# Gets a Card instance from its textual representation.
	# First character: suit
	# Second character: rank
	# Third character: deck
	def from_rsd(cls, s):
		return cls(s[0],s[1],s[2])

	def __str__(self):
		return self.rank+self.suit+str(self.deck)

	def __cmp__(self, other):
		r1 = Card.RANKS.find(self.rank)
		r2 = Card.RANKS.find(other.rank)
		if(r1 == r2):
			s1 = Card.SUITS.find(self.suit)
			s2 = Card.SUITS.find(other.suit)
			return s1 - s2
		else:
			return r1 - r2

	def is_remover(self):
		return str(self) in Card.REMOVERS

	def is_joker(self):
		return str(self) in Card.JOKERS

	def image_file_name(self):
		s = "cards/"
		s += self.suit.lower()
		s += self.rank.lower()
		if self.rank == "J":
			s += str(self.deck)
		s += ".png.gif"
		return s

class Hand:

	def __init__(self, cards):
		self.cards = cards
		self.length = len(cards)

	@classmethod
	def from_rsds(cls, s):
		cards = [Card.from_rsd(c) for c in s]
		return cls(cards)

	def __str__(self):
		s = "["
		for i in range(self.length):
			if i > 0:
				s = s + ", "
			s = s + str(self.cards[i])
		s = s+"]"
		return s

	def add_rsd(self, rsd):
		card = Card.from_rsd(rsd)
		self.add_card(card)

	def add_card(self, card):
		self.length = self.length + 1
		self.cards.append(card)

	def contains_rsd(self, rsd):
		card = Card.from_rsd(rsd)
		return self.contains_card(card)

	def contains_card(self, card):
		return card in self.cards

	def contains_remover(self):
		for c in self.cards:
			if c.is_remover():
				return True
		return False

	def contains_joker(self):
		for c in self.cards:
			if c.is_joker():
				return True
		return False

	def play_rsd(self, rsd):
		for i in range(self.length):
			c = self.cards[i]
			if c == Card.from_rsd(rsd):
				self.length = self.length - 1
				return self.cards.pop(i)

	def play_remover(self):
		for i in range(self.length):
			c = self.cards[i]
			if c.is_remover():
				self.length = self.length - 1
				return self.cards.pop(i)

	def play_joker(self):
		for i in range(self.length):
			c = self.cards[i]
			if c.is_joker():
				self.length = self.length - 1
				return self.cards.pop(i)

class Game:
	DECK = [''.join(card) for card in itertools.product(Card.RANKS, Card.SUITS, Card.DECKS)]
	BOARD = [''.join(card) for card in itertools.product(Card.RANKS.replace("J",""), Card.SUITS, Card.DECKS)]
	WIDTH = 10
	HEIGHT = 10
	LIMIT = 2

	# Two Players: Seven cards each
	# Four Players: Six cards each
	# Six Players: Five cards each
	# Eight Players: Four cards each
	# Ten Players: Three cards each
	# Twelve Players: Three cards each
	def __init__(self, players, ai):
		if players % 2 != 0:
			raise Exception("Invalid number of players")

		self.ai = ai

		self.deck = Game.DECK
		random.shuffle(self.deck)
		hands = [[] for i in range(players)]
		amm = {
			2: 7,
			4: 6,
			6: 5,
			8: 4,
			10: 3,
			12: 3
		}[players]

		for i in range(amm):
			for j in hands:
				j.append(self.deck.pop())

		self.players = []
		for i in range(players):
			self.players.append(Hand.from_rsds(hands[i]))

		# Each position in the board is a tuple with the following:
		# The card in that position or '*' in case of a corner
		# 0/1 if there is a chip on that position (depending on the team). None if it's empty
		# true if the position is part of a sequence (meaning it's "locked"). false if it's still playable
		board = Game.BOARD
		random.shuffle(board)
		self.board = []
		for i in range(Game.WIDTH):
			row = []
			for j in range(Game.HEIGHT):
				if (i == 0 or i == Game.WIDTH-1) and (j == 0 or j == Game.HEIGHT-1):
					row.append(['*',None,False])
				else:
					row.append([board.pop(),None,False])
			self.board.append(row)

		self.current_player = 0
		self.score = [0, 0]

	def is_valid(self, play_x, play_y):
		position = self.board[play_x][play_y]
		team = self.current_player % 2
		hand = self.players[self.current_player]

		# If it's a corner
		if position[0] == '*':
			return (False, '*') # Is corner (has '*')
		# If it's part of a sequence
		if position[2]:
			return (False, 'S') # Sequence
		# If it's a taken position
		if position[1] != None:
			# If it's by the player's team, it's not worth it
			if position[1] == team:
				return (False, 'O') # Own
			# If it's by the other team, see if there's a remover in the hand
			else:
				if not hand.contains_remover():
					return (False, 'T') # Taken, no remover
				else:
					return (True, 'T') # Taken, has remover
		# If it's an available position
		else:
			# See if player has the card or a joker
			card = position[0]
			if not (hand.contains_rsd(card) or hand.contains_joker()):
				return (False, 'P') # Playable
			else:
				if hand.contains_rsd(card):
					return (True, 'C') # Card
				else:
					return (True, 'J') # Joker

		return (True, 'P')

	# Checks for any sequences made by placing a chip on a position x,y on the board and updates the score.
	# Important, in case there was a sequence nearby, only one chip from said sequence may be used in a new sequence.
	# Also, one play may achieve more than one sequence. We'll check for that, too.
	def check_sequence(self, position_x, position_y):
		team = self.current_player % 2
		# Check vertically
		sweep_from = max(position_y-4, 0)
		sweep_to = min(Game.HEIGHT-1,position_y+4)
		sweepers = sweep_to - sweep_from
		if sweepers >= 4:
			for i in range(sweepers-3):
				sequence = True
				use_fixed = True # Can I still use a previously incorporated chip
				start = sweep_from+i
				for j in range(5):
					position = self.board[position_x][start+j]
					if position[0] == "*":
						continue
					if position[1] != team:	# If occupied by the other team's chip
						sequence = False
						break
					else:
						if position[2]:
							if use_fixed:
								use_fixed = False
							else:
								sequence = False
								break
				if sequence:
					self.score[team] = self.score[team] + 1
					for j in range(5):
						self.board[position_x][start+j][2] = True

		# Check horizontally
		sweep_from = max(position_x-4, 0)
		sweep_to = min(Game.WIDTH-1,position_x+4)
		sweepers = sweep_to - sweep_from
		if sweepers >= 4:
			for i in range(sweepers-3):
				sequence = True
				use_fixed = True # Can I still use a previously incorporated chip
				start = sweep_from+i
				for j in range(5):
					position = self.board[start+j][position_y]
					if position[0] == "*":
						continue
					if position[1] != team:	# If occupied by the other team's chip
						sequence = False
						break
					else:
						if position[2]:
							if use_fixed:
								use_fixed = False
							else:
								sequence = False
								break
				if sequence:
					self.score[team] = self.score[team] + 1
					for j in range(5):
						self.board[start+j][position_y][2] = True

		# Check diagonally
		sweep_from_x = max(position_x-4, 0)
		diff_from_x = position_x - sweep_from_x
		sweep_to_x = min(Game.WIDTH-1,position_x+4)
		diff_to_x = sweep_to_x - position_x

		sweep_from_y = max(position_y-4, 0)
		diff_from_y = position_y - sweep_from_y
		sweep_to_y = min(Game.HEIGHT-1,position_y+4)
		diff_to_y = sweep_to_y - position_y

		if diff_from_y < diff_from_x:
			sweep_from_x = position_x - diff_from_y
		else:
			sweep_from_y = position_y - diff_from_x
		if diff_to_y < diff_to_x:
			sweep_to_x = position_x + diff_to_y
		else:
			sweep_to_y = position_y + diff_to_x
		sweepers_x = sweep_to_x - sweep_from_x
		sweepers_y = sweep_to_y - sweep_from_y
		sweepers = min(sweepers_x, sweepers_y)

		if sweepers >= 4:
			# Left to Right, Top to bottom
			for i in range(sweepers-3):
				sequence = True
				use_fixed = True # Can I still use a previously incorporated chip
				start_x = sweep_from_x+i
				start_y = sweep_from_y+i
				for j in range(5):
					position = self.board[start_x+j][start_y+j]
					if position[0] == "*":
						continue
					if position[1] != team:	# If occupied by the other team's chip
						sequence = False
						break
					else:
						if position[2]:
							if use_fixed:
								use_fixed = False
							else:
								sequence = False
								break
				if sequence:
					self.score[team] = self.score[team] + 1
					start_x = sweep_from_x+i
					start_y = sweep_from_y+i
					for j in range(5):
						self.board[start_x+j][start_y+j][2] = True

		# sweep_from_x = max(position_x-4, 0)
		# diff_from_x = position_x - sweep_from_x
		# sweep_to_x = min(Game.WIDTH-1,position_x+4)
		# diff_to_x = sweep_to_x - position_x

		# sweep_from_y = max(position_y-4, 0)
		# diff_from_y = position_y - sweep_from_y
		# sweep_to_y = min(Game.HEIGHT-1,position_y+4)
		# diff_to_y = sweep_to_y - position_y

		# if diff_from_y < diff_to_x:
		# 	sweep_from_x = position_x - diff_from_y
		# else:
		# 	sweep_from_y = position_y - diff_to_x
		# if diff_to_y < diff_from_x:
		# 	sweep_to_x = position_x + diff_to_y
		# else:
		# 	sweep_to_y = position_y + diff_from_x
		# sweepers_x = sweep_to_x - sweep_from_x
		# sweepers_y = sweep_to_y - sweep_from_y
		# sweepers = min(sweepers_x, sweepers_y)

		# if sweepers >= 4:
		# 	# Right to Left, Top to bottom
		# 	for i in range(sweepers-3):
		# 		sequence = True
		# 		use_fixed = True # Can I still use a previously incorporated chip
		# 		start_x = sweep_to_x-i
		# 		start_y = sweep_from_y+i
		# 		for j in range(5):
		# 			print str(start_x-j)
		# 			print str(start_y+j)
		# 			position = self.board[start_x-j][start_y+j]
		# 			if position[0] == "*":
		# 				continue
		# 			if position[1] != team:	# If occupied by the other team's chip
		# 				sequence = False
		# 				break
		# 			else:
		# 				if position[2]:
		# 					if use_fixed:
		# 						use_fixed = False
		# 					else:
		# 						sequence = False
		# 						break
		# 		if sequence:
		# 			self.score[team] = self.score[team] + 1
		# 			start_x = sweep_to_x-i
		# 			start_y = sweep_from_y+i
		# 			for j in range(5):
		# 				self.board[start_x-j][start_y+j][2] = True


	def card_is_playable(self, rsd):
		if rsd[0] == "J":
			return True
		still_can_make_it = True
		for column in self.board:
			for position in column:
				if position[0] == rsd:
					if position[1] == None:
						return True
					else:
						if still_can_make_it:
							still_can_make_it = False
						else:
							return False
		return False

	def fitness(self, chromosome):
		position_x = Chromosome.decode(chromosome.chain[:4])
		position_y = Chromosome.decode(chromosome.chain[4:])

		if position_x > 9 or position_y > 9:
			return 0
		if not self.is_valid(position_x, position_y)[0]:
			return 0

		team = self.current_player % len(self.players)

		n = max(position_y - 4, 0)
		s = min(position_y + 5, Game.HEIGHT)
		w = max(position_x - 4, 0)
		e = min(position_x + 5, Game.WIDTH)

		near_ns = 0
		near_we = 0
		near_tlbr = 0
		near_trbl = 0

		other_ns = 0
		other_we = 0
		other_tlbr = 0
		other_trbl = 0

		# ns
		for y in range(n, s):
			position = self.board[position_x][y]
			if(position[1] == team):
				near_ns = near_ns + 1
			elif(position[1] != None and position[1] != team):
				other_ns = other_ns + 1
		#ew
		for x in range(w, e):
			position = self.board[x][position_y]
			if(position[1] == team):
				near_we = near_we + 1
			elif(position[1] != None and position[1] != team):
				other_we = other_we + 1

		for x in range(w, e):
			for y in range(n, s):
				position = self.board[x][y]
				if(position[1] == team):
					near_tlbr = near_tlbr + 1
				elif(position[1] != None and position[1] != team):
					other_tlbr = other_tlbr + 1

		for x in reversed(range(w, e)):
			for y in range(n, s):
				position = self.board[x][y]
				if(position[1] == team):
					near_trbl = near_trbl + 1
				elif(position[1] != None and position[1] != team):
					other_trbl = other_trbl + 1

		fitness = 1
		fitness = fitness + near_ns**2
		fitness = fitness + near_we**2
		fitness = fitness + near_tlbr**2
		fitness = fitness + near_trbl**2

		fitness = fitness + other_ns**3
		fitness = fitness + other_we**3
		fitness = fitness + other_tlbr**3
		fitness = fitness + other_trbl**3

		return int(fitness)

	def random_fitness(self, asdf):
		return int(random.random() * 10)

	def turn(self):
		team = self.current_player % 2

		print "* --------------------------------------------------"
		print "* It's Player "+str(self.current_player+1)+"'s turn!"
		print "* You play for Team "+str(team+1)
		print

		play_x = None
		play_y = None

		if self.ai[self.current_player]:
			valid = (False, 'R')
			while( not valid[0] ):
				if(self.ai[self.current_player] == "R"):
					fitness_function = self.random_fitness
				else:
					fitness_function = self.fitness
				gen_alg = Pool(8, 15, 0.7, 0.001, fitness_function)
				gen_alg.evolve(800)
				gen_ans = gen_alg.pick().chain
				play_x = min(Chromosome.decode(gen_ans[:4]), 9)
				play_y = min(Chromosome.decode(gen_ans[4:]), 9)
				valid = self.is_valid(play_x, play_y)

			print "AI chose: (" + str(play_x+1) + ", " + str(play_y+1) + ")"
			print

		else:
			play_x = int(raw_input("Position to play [x]: ")) - 1
			play_y = int(raw_input("Position to play [y]: ")) - 1
			valid = self.is_valid(play_x, play_y)
			# valid = (True, 'C')
			while( not valid[0] ):
				print "You can't play that position. Please try again."
				play_x = int(raw_input("Position to play [x]: ")) - 1
				play_y = int(raw_input("Position to play [y]: ")) - 1
				valid = self.is_valid(play_x, play_y)

		position = self.board[play_x][play_y]

		played = None
		print valid[1], [str(c) for c in self.players[self.current_player].cards]
		# Gets the card first
		if valid[1] == 'T': # We'll play with a remover
			played = self.players[self.current_player].play_remover()
		elif valid[1] == 'C': # We'll play with a regular card
			played = self.players[self.current_player].play_rsd(position[0])
		elif valid[1] == 'J': # We'll play with a joker
			played = self.players[self.current_player].play_joker()

		print "Filled: " + position[0]
		print "Card played: " + str(played)
		print

		# Puts or removes the chip in the position
		if valid[1] == 'T': # We'll play with a remover
			self.board[play_x][play_y][1] = None
		elif valid[1] == 'C': # We'll play with a regular card
			self.board[play_x][play_y][1] = team
		elif valid[1] == 'J': # We'll play with a joker
			self.board[play_x][play_y][1] = team

		# Check for sequences
		self.check_sequence(play_x,play_y)

		# Draws a card
		draw = self.deck.pop()
		orig_draw = draw
		while(not self.card_is_playable(draw)):
			print "'" + str(draw) + "' is not playable. Drawing a new card..."
			print
			self.deck = [draw] + self.deck
			draw = self.deck.pop()
			if draw == orig_draw:
				print "No more playable cards. The game is over!"
				break
		self.players[self.current_player].add_rsd(draw)

		print "The score is"
		print "Team 1: " + str(self.score[0])
		print "Team 2: " + str(self.score[1])
		print

		# Next player!
		self.current_player = self.current_player + 1
		self.current_player = self.current_player % len(self.players)

	def finished(self):
		for score in self.score:
			if score >= Game.LIMIT:
				return True
		return False

class Sequence(tk.Frame):

	CARD_WIDTH = 71
	CARD_HEIGHT = 96

	def __init__(self, parent):
		self.parent = parent
		self.rows = Game.WIDTH+2
		self.columns = Game.HEIGHT

		players = int(raw_input("¿How many players? [Even numbers between 2-12]: "))
		while players < 2 or players > 12 or players % 2 != 0:
			print "Invalid ammount"
			players = int(raw_input("¿How many players? [Even numbers between 2-12]: "))
		print

		ai = []
		for i in range(players):
			is_ai = raw_input("Is player " + str(i) + " CPU? [Y/y = yes, R/r = random, anything else means no]: ").lower()
			if(is_ai == "y"):
				ai.append("G")
			elif(is_ai == "r"):
				ai.append("R")
			else:
				ai.append(false)
		print

		self.game = Game(players, ai)

		tk.Frame.__init__(self, parent)

		canvas_width = (self.rows+1) * (Sequence.CARD_WIDTH) + 30
		canvas_height = self.columns * (Sequence.CARD_HEIGHT) + 30

		self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0,width=canvas_width,
			height=canvas_height, background="gray")
		self.canvas.pack(side="top", fill="both", expand=True, padx=2, pady=2)

		self.refresh()

	def refresh(self):
		self.canvas.delete("all")
		# Adds captions
		for i in range(Game.WIDTH):
			pos = i*Sequence.CARD_WIDTH + (Sequence.CARD_WIDTH/2)
			self.canvas.create_text((30+pos, 15), text=str(i+1))

		for i in range(Game.HEIGHT):
			pos = i*Sequence.CARD_HEIGHT + (Sequence.CARD_HEIGHT/2)
			self.canvas.create_text((15, 30+pos), text=str(i+1))

		handcaptionposition = (Game.WIDTH + 1)*Sequence.CARD_WIDTH+30+(Sequence.CARD_WIDTH/2)
		self.canvas.create_text((handcaptionposition, 15), text="Player "+str(self.game.current_player+1))

		# Draws the board
		x = 0
		self.img = []
		for column in self.game.board:
			y = 0
			self.img.append([])
			for row in column:
				card = row[0]
				pos_x = (x*Sequence.CARD_WIDTH)+30
				pos_y = (y*Sequence.CARD_HEIGHT)+30

				image = "cards/*.png.gif"
				if card != "*":
					image = Card.from_rsd(card).image_file_name()
				self.img[x].append(tk.PhotoImage(file=image))
				self.canvas.create_image((pos_x,pos_y),image=self.img[x][y],anchor=tk.NW)

				if row[1] != None:
					color = "blue"
					if row[2]:
						color = "#0000AA"
					if row[1] == 1:
						color = "red"
						if row[2]:
							color = "#CC0000"
					self.canvas.create_oval(pos_x+10, pos_y+23, pos_x+60, pos_y+73, outline="black",fill=color)

				y = y+1
			x = x+1

		# Draws the player's hand
		hand = self.game.players[self.game.current_player]
		self.handimgs = []
		pos_x = (Game.WIDTH + 1)*Sequence.CARD_WIDTH+30
		pos_y = 30
		for i in range(hand.length):
			card = hand.cards[i]
			image = card.image_file_name()
			self.handimgs.append(tk.PhotoImage(file=image))
			self.canvas.create_image((pos_x,pos_y),image=self.handimgs[i],anchor=tk.NW)
			pos_y = pos_y + Sequence.CARD_HEIGHT

		if not self.game.finished():
			self.parent.after(1000, self.loop)

	def loop(self):
		self.game.turn()
		self.refresh()

print "* --------------------------------------------------"
print "* Sequence + A.I. (by aleknaui)"
print "* --------------------------------------------------"
print

root = tk.Tk()
root.resizable(0,0)
board = Sequence(root)
board.pack(side="top", fill="both", expand="true", padx=4, pady=4)
root.mainloop()