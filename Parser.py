#!/usr/bin/python3

from parsec import *

def parse_crn(source_code):
	def r(v):
		e = StopIteration(v)
		e.value = v
		raise e

	# This should import from parsec but gives ImportError for no obvious reason
	def optional(p, default_value=None):
		@Parser
		def optional_parser(text, index):
			res = p(text, index)
			return Value.success(res.index, res.value if res.status else default_value)
		return optional_parser

	whitespace = regex(r'\s*')
	# Incorporates comments
	whitespace_newlines = regex(r'\s*(#[^\n]*\s*)*', re.MULTILINE)

	lexeme = lambda p: p << whitespace

	newline = lexeme(string('\n'))
	arrow = lexeme(string('->'))
	colon = lexeme(string(':'))
	plus = lexeme(string('+'))
	pling = lexeme(string('!'))
	natural = lexeme(regex(r'[0-9]+')).parsecmap(int)
	simpleatom = lexeme(regex('[A-Za-z_][0-9A-Za-z_]*'))

	simple_char = regex(r'[^"\\]+')
	escaped_char = string('\\') >> (
		string('\\')
		| string('/')
		| string('"')
		| string('b').result('\b')
		| string('f').result('\f')
		| string('n').result('\n')
		| string('r').result('\r')
		| string('t').result('\t')
		| regex(r'u[0-9a-fA-F]{4}').parsecmap(lambda s: chr(int(s[1:], 16)))
	)

	@lexeme
	@generate
	def quoted():
		yield string('"')
		body = yield many(simple_char | escaped_char)
		yield string('"')
		r(''.join(body))

	@lexeme
	@generate
	def out_string():
		yield string('Out_')
		value = yield quoted
		r(('*Str', value))

	@lexeme
	@generate
	def in_atom():
		yield string('In_')
		value = yield simpleatom
		r(('*In', value))

	@lexeme
	@generate
	def out_atom():
		yield string('Out_')
		value = yield simpleatom
		r(('*Out', value))

	atom = in_atom ^ out_atom ^ out_string ^ simpleatom

	@generate
	def simpleatom_count():
		count = yield optional(natural, 1)
		theatom = yield simpleatom
		r((theatom, count))

	@generate
	def atom_count():
		count = yield optional(natural, 1)
		theatom = yield atom
		r((theatom, count) if isinstance(theatom, str) else theatom)

	@generate
	def lhs():
		merged = dict()
		atom_counts = yield sepBy(simpleatom_count, plus)
		for atom, count in atom_counts:
			merged[atom] = count + merged.get(atom, 0)
		r(merged)

	@generate
	def rule():
		inputs = yield lhs
		yield arrow
		outputs = yield sepBy(atom_count, plus)
		r((inputs, outputs))

	@generate
	def initial_value():
		yield pling
		inputs = yield lhs
		r(inputs)

	@generate
	def program():
		yield(whitespace_newlines)
		rules = yield(sepEndBy(rule, whitespace_newlines))
		initial_values = yield optional(initial_value)
		if initial_values == None:
			initial_values = dict()
		r((rules, initial_values))

	return program.parse(source_code)
