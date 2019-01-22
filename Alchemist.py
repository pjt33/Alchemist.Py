#!/usr/bin/python3

import random
import sys
from Parser import parse_crn


def is_applicable(rule, state):
	for atom, count in rule[0].items():
		available = state.get(atom, 0)
		if (count == 0 and available != 0) or count > available:
			return False
	return True


def max_repetition_count(rule, state):
	'''Assumes that is_applicable(rule, state) has already been checked'''
	consumption = rule[0].copy()
	for atom, count in rule[1]:
		# Special case: I/O and repetition is messier than I want
		if atom[0] == '*':
			return 1

		if atom in consumption:
			consumption[atom] -= count

	minmax = float('+inf')
	for atom, consumed in consumption.items():
		if consumed > 0:
			available = state.get(atom, 0)
			minmax = min(minmax, available // consumed)

	assert minmax > 0
	
	# If the rule could be applied arbitrarily many times, either we have an infinite loop
	# or there's more than one applicable rule and the other one will break the loop.
	# In the interests of not mixing floats and big integers, pick a random number.
	if minmax == float('+inf'):
		return random.randrange(65536)

	return minmax


def apply_rule(rule, state, repetition_count):
	for atom, count in rule[0].items():
		surplus = state.get(atom, 0) - count * repetition_count
		if surplus != 0:
			state[atom] = surplus
		elif atom in state:
			del state[atom]

	# Apply the output items in order
	for atom, count in rule[1]:
		if atom[0] != '*':
			state[atom] = state.get(atom, 0) + count * repetition_count
		elif atom == '*In':
			# Ensure that any prompt has been written before taking input
			sys.stdout.flush()
			state[count] = state.get(count, 0) + int(input())
		elif atom == '*Out':
			print(state.get(count, 0), end='')
		elif atom == '*Str':
			print(count, end='')
		else:
			raise Exception("Unexpected atom: " + atom)

	return state


if __name__ == '__main__':
	source_code = open(sys.argv[1]).read()
	rules, state = parse_crn(source_code)

	# Special case for bootstrapping
	state['_'] = 1 + state.get('_', 0)

	while True:
		applicable = [rule for rule in rules if is_applicable(rule, state)]
		if len(applicable) == 0:
			break

		active_rule = random.choice(applicable)

		# Optimisation: if we can apply it more than once, apply it more than once
		# NB It may prove desirable to add an extra condition here that forces
		# repetition_count to 1 if len(applicable) > 1 for reliable probabilistic
		# programs.
		repetition_count = max_repetition_count(active_rule, state)
		state = apply_rule(active_rule, state, repetition_count)
