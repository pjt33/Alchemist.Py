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
	whitespace_newlines = regex(r'\s*', re.MULTILINE)

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

	atom = in_atom | (out_atom ^ out_string) | simpleatom

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


	def pairs_to_dict(pairs):
		return dict((x, y) for x, y in pairs)

	@generate
	def rule():
		inputs = yield sepBy(simpleatom_count, plus)
		yield arrow
		outputs = yield sepBy(atom_count, plus)
		r((pairs_to_dict(inputs), pairs_to_dict(outputs)))

	@generate
	def initial_value():
		yield pling
		theatom = yield simpleatom
		yield colon
		count = yield natural
		r((theatom, count))

	@generate
	def program():
		yield(whitespace_newlines)
		rules = yield(sepEndBy(rule, whitespace_newlines))
		initial_values = yield many(initial_value)
		r((rules, pairs_to_dict(initial_values)))

	return program.parse(source_code)
