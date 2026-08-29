# [?] CL-2021-30: BLS: Public key aggregation ambiguous infinite points handling

## Summary
Severity: Unknown
Chain: Ethereum (consensus layer)
Component: Teku
Published: 2021-12-01
Source: https://github.com/ConsenSys/teku/issues/4111
Type: ef-disclosure

## Details
Affected Clients: Teku
Uid: CL-2021-30
Bug: BLS: Public key aggregation ambiguous infinite points handling
Type: Crypto
Summary: BlstPublicKey.aggregate() will return infinitePublicKey in two cases:<br><br>If one of the public keys to aggregate is invalid (not in the subgroup or infinity point)<br>If the sum of (valid) public keys happens to be zero<br>
Links: [https://github.com/ConsenSys/teku/issues/4111](https://github.com/ConsenSys/teku/issues/4111)
Reported: 2021-06-24
Fixed Date: 2021-09-21
Published: 2021-12-01
Bounty Hunter: Taurus
Bounty Points: Part of EF initiated Security Audit: https://arxiv.org/abs/2109.11685
Bounty Reward (Usd): 0
