# [?] CL-2021-26: BLS: No BLS public key validation due to validate parameter missing

## Summary
Severity: Unknown
Chain: Ethereum (consensus layer)
Component: Lodestar
Published: 2021-12-01
Source: https://github.com/ChainSafe/lodestar/issues/2555
Type: ef-disclosure

## Details
Affected Clients: Lodestar
Uid: CL-2021-26
Bug: BLS: No BLS public key validation due to validate parameter missing
Type: Crypto
Summary: To create a public key BLS spec requires first validate the public key bytes.<br>To validate the input bytes fromBytes must be called as fromBytes(bytes, type, true).<br><br>The following fragments call fromBytes without validation:<br><br>https://github.com/ChainSafe/lodestar/blob/master/packages/lodestar/src/chain/bls/multithread/worker.ts#L39<br>[https://github.com/ChainSafe/lodestar/blob/master/packages/lodestar/src/chain/bls/multithread/worker.ts#L53](https://github.com/ChainSafe/lodestar/blob/master/packages/lodestar/src/chain/bls/multithread/worker.ts#L53)
Links: [https://github.com/ChainSafe/lodestar/issues/2555](https://github.com/ChainSafe/lodestar/issues/2555)
Reported: 2021-05-24
Fixed Date: 2021-09-22
Published: 2021-12-01
Bounty Hunter: Taurus
Bounty Points: Part of EF initiated Security Audit: https://arxiv.org/abs/2109.11685
Bounty Reward (Usd): 0
