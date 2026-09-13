# [?] p2p/simulations: fix unlikely crash in probabilistic connect (#23200)

## Summary
Severity: Unknown
Chain: Celo
Component: celo-org/celo-blockchain
Published: 2021-07-29
Source: https://github.com/celo-org/celo-blockchain/commit/8f11d279d241cfdf2571d4fa772dc38efc6175d0
Type: security-commit

## Details
p2p/simulations: fix unlikely crash in probabilistic connect (#23200)

When the nodeCount is less than 10, it will panic with the out of bound error.
How about we just skip this round, when rand1 and rand2 are equal?
