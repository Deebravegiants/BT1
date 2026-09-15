# [H] CL-2020-07: DoS Attack via gossipsub

## Summary
Severity: High
Chain: Ethereum (consensus layer)
Component: Teku
Published: 2021-12-01
Source: https://github.com/ethereum/public-attacknets/issues/15
Type: ef-disclosure

## Details
Affected Clients: Teku
Uid: CL-2020-07
Bug: DoS Attack via gossipsub
Type: DoS
Summary: Teku nodes are vulnerable to a resource exhaustion attack caused by allocating a buffer from an unchecked attacker-controlled length field causing a DoS condition that prevents them from participating in consensus.
Links: [https://github.com/ethereum/public-attacknets/issues/15](https://github.com/ethereum/public-attacknets/issues/15)
Reported: 2020-09-04
Fixed Date: 2020-09-04
Published: 2021-12-01
Severity: High
Bounty Hunter: Tintin
Bounty Points: 2500
Bounty Reward (Usd): 5000
