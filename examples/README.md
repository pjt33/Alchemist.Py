### Josephus

The [Josephus problem](//en.wikipedia.org/wiki/Josephus_problem).
Input is n (number of soldiers) and k (advance) and output is the (zero-indexed) position of the person who survives.
E.g. with input

    40
    3

the expected output is

    27

### SideEffects

Tests that side-effects are applied left-to-right and output doesn't include implicit newlines. Expected output: `13`

### Initialiser

Tests that the parser handles inline initialisation of the state. Expected output: `3`
