# [?] CL-2020-34: BLS: Missing check on seed and password length

## Summary
Severity: Unknown
Chain: Ethereum (consensus layer)
Component: Lighthouse
Published: 2021-12-01
Source: https://github.com/sigp/lighthouse/issues/2102
Type: ef-disclosure

## Details
Affected Clients: Lighthouse
Uid: CL-2020-34
Bug: BLS: Missing check on seed and password length
Type: Bug
Summary: This is called in wallet.rs, where a wallet can be created from non-empty seed and password of any size (no length check inWalletBuilder::from\_seed\_bytes()):
Links: [https://github.com/sigp/lighthouse/issues/2102](https://github.com/sigp/lighthouse/issues/2102)
Reported: 2020-12-18
Published: 2021-12-01
Bounty Hunter: Taurus
Bounty Points: Part of EF initiated Security Audit: https://arxiv.org/abs/2109.11683
Bounty Reward (Usd): 0
