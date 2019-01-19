#!/usr/bin/python3

import random
import sys
from Parser import parse_crn


def is_applicable(rule, state):
	for atom, count in rule[0].items():
		if (count == 0 and state.get(atom, 0) != 0) or count > state.get(atom, 0):
			return False
	return True


def max_repetition_count(rule, state):
	minmax = float('+inf')
	for atom, count in rule[0].items():
		available = state.get(atom, 0)
		if (count == 0 and available != 0) or count > available:
			return 0
		consumption = count - rule[1].get(atom, 0)
		if consumption > 0:
			minmax = min(minmax, available // consumption)

	assert minmax > 0
	# Special case: I/O and repetition is messier than I want
	if '*In' in rule[1] or '*Out' in rule[1] or '*Str' in rule[1]:
		return 1

	return minmax


def apply_rule(rule, state, repetition_count):
	for atom, count in rule[0].items():
		surplus = state.get(atom, 0) - count * repetition_count
		if surplus != 0:
			state[atom] = surplus
		elif atom in state:
			del state[atom]

	for atom, count in rule[1].items():
		if atom[0] != '*':
			state[atom] = state.get(atom, 0) + count * repetition_count
		elif atom == '*In':
			state[count] = state.get(count, 0) + int(input())
		elif atom == '*Out':
			print(state.get(count, 0))
		elif atom == '*Str':
			print(count)
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
		repetition_count = max_repetition_count(active_rule, state)
		state = apply_rule(active_rule, state, repetition_count)
