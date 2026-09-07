# [?] CL-2021-31: BLS: Detect unsafe coefficients in fast BLS verification

## Summary
Severity: Unknown
Chain: Ethereum (consensus layer)
Component: Teku
Published: 2021-12-01
Source: https://github.com/ConsenSys/teku/issues/4112
Type: ef-disclosure

## Details
Affected Clients: Teku
Uid: CL-2021-31
Bug: BLS: Detect unsafe coefficients in fast BLS verification
Type: Crypto
Summary: In the implementation of https://ethresear.ch/t/fast-verification-of-multiple-bls-signatures/5407, a zero coefficient would allow the verification of signatures including an invalid one (if assigned a zero r\_i).<br><br>If the PRNG behaves correctly, the chance of this happening is negligible, but since a non-crypto PRNG is used, and as defense-in-depth measure (along the same lines as ECDSA checks), I would recommend to enforce non-zeroness in:
Links: [https://github.com/ConsenSys/teku/issues/4112](https://github.com/ConsenSys/teku/issues/4112)
Reported: 2021-06-24
Fixed Date: 2021-06-28
Published: 2021-12-01
Bounty Hunter: Taurus
Bounty Points: Part of EF initiated Security Audit: https://arxiv.org/abs/2109.11685
Bounty Reward (Usd): 0
