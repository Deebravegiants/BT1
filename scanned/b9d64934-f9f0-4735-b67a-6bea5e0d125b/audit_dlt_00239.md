# [?] CL-2021-17: BLS: Missing input validation in SecretKeyFromBigNum

## Summary
Severity: Unknown
Chain: Ethereum (consensus layer)
Component: Prysm
Published: 2021-12-01
Source: https://github.com/prysmaticlabs/prysm/issues/8819
Type: ef-disclosure

## Details
Affected Clients: Prysm
Uid: CL-2021-17
Bug: BLS: Missing input validation in SecretKeyFromBigNum
Type: Crypto
Summary: BLS's SecretKeyFromBigNum is an exported function that creates a BLS private key. It can be misused as follows:<br>SecretKeyFromBigNum("1") will produce a BLS private key consisting of 31 zero bytes.
Links: [https://github.com/prysmaticlabs/prysm/issues/8819](https://github.com/prysmaticlabs/prysm/issues/8819)
Reported: 2021-04-26
Fixed Date: 2021-04-27
Published: 2021-12-01
Bounty Hunter: Taurus
Bounty Points: Part of EF initiated Security Audit: https://arxiv.org/abs/2109.11685
Bounty Reward (Usd): 0
