# [?] p2p/enode: avoid crashing for invalid IP (#21981)

## Summary
Severity: Unknown
Chain: Celo
Component: celo-org/celo-blockchain
Published: 2020-12-09
Source: https://github.com/celo-org/celo-blockchain/commit/817a3fb5622c8704116e9847661c16f9f3d785c6
Type: security-commit

## Details
p2p/enode: avoid crashing for invalid IP (#21981)

The database panicked for invalid IPs. This is usually no problem
because all code paths leading to node DB access verify the IP, but it's
dangerous because improper validation can turn this panic into a DoS
vulnerability. The quick fix here is to just turn database accesses
using invalid IP into a noop. This isn't great, but I'm planning to
remove the node DB for discv5 long-term, so it should be fine to have
this quick fix for half a year.

Fixes #21849
