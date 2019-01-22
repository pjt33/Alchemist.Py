# [Alchemist](https://esolangs.org/wiki/Alchemist) - a non-deterministic esolang based on chemical reaction networks

This is a Python implementation from the spec. It is almost certainly not exactly feature-compatible with the [official implementation](//github.com/bforte/Alchemist).

## Known quirks

* The string syntax parsed does not include the full set of escapes supported by the specification and reference implementation, which both use Haskell strings.
* Currently there is no support for seeding the random number generator for repeatable testing of non-deterministic programs.
* There is not support for the various command-line options supported by the reference implementation.
* Comments are not specified, but the reference implementation supports `#` as a comment start symbol, with a newline ending the comment, and this implementation also supports it.

## Programming notes

### Comments

Although this implementation supports `#` for comments, the spec-compliant way of writing a comment is

    Comment -> Out_"Comment text goes here"

### Alchemist as an extension of Minsky register machines

The computational model is basically that of Minsky, as described [here](//codegolf.stackexchange.com/q/1864/194). A Minsky RM program can be converted into an Alchemist program very simply: a state `q: a + r` becomes a rule `Q -> A + R`; and a state `q: a - s t` becomes two rules: `Q A -> S` and `Q 0A -> T`. Optimisations can then be applied to reduce chains of rules to single rules. The representation of both states and registers as atoms nicely exposes the equivalence of code and data.

The real departure from the Minsky RM is the addition of non-determinism.

However, from a programming praxis perspective there is another nice feature of Alchemist. The state is not constrained to be represented by one atom: we can use a tuple of atoms, and this allows (non-recursive) subroutines. If the sequence of states between `q` and `r` is identical to the sequence of states between `s` and `t` then we can represent `q` as `Q SUB`, `s` as `S SUB`; implement the sequence between states `SUB` and `RET`; and then define rules `Q + RET -> R` and `S + RET -> T`.

## Roadmap

* Optimise the ruleset by deleting unreachable rules
* It would be interesting to extend the language to support an import feature for libraries. For maximum utility this could allow atom substitutions, so that libraries act as macros with arguments.
* Play around with non-deterministic programs and determine whether the speed optimisations come at a cost of the ability to analyse programs.
