# [?] CL-2021-25: BLS:<br>Incorrect result for zero lengths arrays in aggregateVerify

## Summary
Severity: Unknown
Chain: Ethereum (consensus layer)
Component: None
Published: 2021-05-27
Source: https://github.com/ChainSafe/blst-ts/issues/43
Type: ef-disclosure

## Details
Affected Clients: None
Uid: CL-2021-25
Bug: BLS:<br>Incorrect result for zero lengths arrays in aggregateVerify
Type: Crypto
Summary: aggregateVerify doesn't check the size of public keys/messages arrays. A zero-length array is possible.
Links: [https://github.com/ChainSafe/blst-ts/issues/43](https://github.com/ChainSafe/blst-ts/issues/43)
Reported: 2021-05-24
Fixed Date: 2021-05-27
Bounty Hunter: Taurus
Bounty Points: Part of EF initiated Security Audit: https://arxiv.org/abs/2109.11682
Bounty Reward (Usd): 0
