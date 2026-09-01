# [?] CL-2021-27: BLS: BLS secret key validation is missing

## Summary
Severity: Unknown
Chain: Ethereum (consensus layer)
Component: None
Published: 2021-12-01
Source: https://github.com/ChainSafe/bls/issues/96
Type: ef-disclosure

## Details
Affected Clients: None
Uid: CL-2021-27
Bug: BLS: BLS secret key validation is missing
Type: Crypto
Summary: The BLS spec requires that the secret key (SK) must be a uniformly random integer such that 1 <= SK < r.<br>Where r is the order curve.<br><br>The last check is missing:<br><br>fromBytes<br>fromBytes<br><br>Expected behavior<br><br>Check that the provided SK < r.
Links: [https://github.com/ChainSafe/bls/issues/96](https://github.com/ChainSafe/bls/issues/96)
Reported: 2021-06-02
Published: 2021-12-01
Bounty Hunter: Taurus
Bounty Points: Part of EF initiated Security Audit: https://arxiv.org/abs/2109.11681
Bounty Reward (Usd): 0
