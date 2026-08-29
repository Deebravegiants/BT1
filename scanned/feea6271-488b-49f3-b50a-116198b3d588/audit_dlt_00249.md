# [?] CL-2021-32: BLS: No length check in AggregatePublicKeys

## Summary
Severity: Unknown
Chain: Ethereum (consensus layer)
Component: Prysm
Published: 2021-12-01
Source: https://github.com/prysmaticlabs/prysm/issues/9091
Type: ef-disclosure

## Details
Affected Clients: Prysm
Uid: CL-2021-32
Bug: BLS: No length check in AggregatePublicKeys
Type: Crypto
Summary: There is no length check in AggregatePublicKeys. If pubs is nil or \[\]\[\]byte{} the function returns a public key without error.
Links: [https://github.com/prysmaticlabs/prysm/issues/9091](https://github.com/prysmaticlabs/prysm/issues/9091)
Reported: 2021-06-24
Fixed Date: 2021-06-27
Published: 2021-12-01
Bounty Hunter: Taurus
Bounty Points: Part of EF initiated Security Audit: https://arxiv.org/abs/2109.11685
Bounty Reward (Usd): 0
