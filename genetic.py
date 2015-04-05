#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random

class Chromosome:
	def __init__(self, chain):
		self.chain = chain
		self.length = len(chain)

	@classmethod
	def cross(cls, parent1, parent2, mutation_rate):
		switch_point = random.choice(range(parent1.length))
		chains = [parent1.chain[:switch_point] + parent2.chain[switch_point:], parent2.chain[:switch_point] + parent1.chain[switch_point:]]
		chain = random.choice(chains)
		i = 0
		while i < parent1.length:
			if random.random() <= mutation_rate:
				chain[i] = (chain[i] + 1) % 1
			i = i + 1
		return cls(chain)

	@classmethod
	def random(cls, length):
		return cls([random.choice([0,1]) for i in range(length)])

	@staticmethod
	def decode(chain):
		base = 1
		x = 0
		for i in chain:
			x = x + (base*i)
			base = base*2
		return x

class Pool:
	def __init__(self, chromosome_length, population_size, crossover_rate, mutation_rate, fitness_function):
		self.population_size = population_size
		self.crossover_rate = crossover_rate
		self.mutation_rate = mutation_rate
		self.fitness_function = fitness_function
		self.max_fitness = float("-inf")
		self.best_chromosome = None

		self.population = []
		while population_size > 0:
			chromosome = Chromosome.random(chromosome_length)
			fitness = self.fitness_function(chromosome)
			while fitness <= 0:
				chromosome = Chromosome.random(chromosome_length)
				fitness = self.fitness_function(chromosome)

			if fitness > self.max_fitness:
				self.max_fitness = fitness
				self.best_chromosome = chromosome
			self.population = self.population + [chromosome]*fitness

			population_size = population_size - 1

	def new_generation(self):
		i = 0
		new_population = []

		parent1 = random.choice(self.population)
		parent2 = random.choice(self.population)
		while i < self.population_size:
			if random.random() <= self.crossover_rate:
				child = Chromosome.cross(parent1, parent2, self.mutation_rate)
				fitness = self.fitness_function(child)
				while fitness <= 0:
					parent2 = random.choice(self.population)
					child = Chromosome.cross(parent1, parent2, self.mutation_rate)
					fitness = self.fitness_function(child)

				if fitness > self.max_fitness:
					self.max_fitness = fitness
					self.best_chromosome = child
				new_population = new_population + [child]*fitness
				# if fitness < 0:
					# new_population.append(child)
				i = i+1
			parent1 = parent2
			parent2 = random.choice(self.population)
		self.population = new_population

	def evolve(self, iterations):
		i = 0
		while i < iterations:
			self.new_generation()
			i = i + 1

	def pick(self):
		return self.best_chromosome #random.choice(self.population)