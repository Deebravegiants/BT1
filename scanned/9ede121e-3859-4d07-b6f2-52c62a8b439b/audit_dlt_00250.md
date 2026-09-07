# [?] CL-2021-33: BLS: Detect unsafe coefficients in verifyMultipleAggregateSignatures

## Summary
Severity: Unknown
Chain: Ethereum (consensus layer)
Component: Prysm
Published: 2021-12-01
Source: https://github.com/prysmaticlabs/prysm/issues/9098
Type: ef-disclosure

## Details
Affected Clients: Prysm
Uid: CL-2021-33
Bug: BLS: Detect unsafe coefficients in verifyMultipleAggregateSignatures
Type: Crypto
Summary: In the implementation of Fast verification of multiple BLS signatures, a zero coefficient would allow the verification of signatures including an invalid one (if assigned a zero r\_i).<br><br>VerifyMultipleSignature's comments say that r\_i must be generated randomly from 1 to max uint64.
Links: [https://github.com/prysmaticlabs/prysm/issues/9098](https://github.com/prysmaticlabs/prysm/issues/9098)
Reported: 2021-06-25
Fixed Date: 2021-06-28
Published: 2021-12-01
Bounty Hunter: Taurus
Bounty Points: Part of EF initiated Security Audit: https://arxiv.org/abs/2109.11685
Bounty Reward (Usd): 0
