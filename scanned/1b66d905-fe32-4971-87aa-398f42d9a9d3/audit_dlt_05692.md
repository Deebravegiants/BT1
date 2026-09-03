# [?] p2p/discover: fix deadlock in discv5 message dispatch (#21858)

## Summary
Severity: Unknown
Chain: Celo
Component: celo-org/celo-blockchain
Published: 2020-11-25
Source: https://github.com/celo-org/celo-blockchain/commit/429e7141f2f41c1d66dd4dd711a47ca9e0f0c2cb
Type: security-commit

## Details
p2p/discover: fix deadlock in discv5 message dispatch (#21858)

This fixes a deadlock that could occur when a response packet arrived
after a call had already received enough responses and was about to
signal completion to the dispatch loop.

Co-authored-by: Felix Lange <fjl@twurst.com>
