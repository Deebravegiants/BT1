# [?] CL-2021-36: Improper nonce handling in Noise handshake

## Summary
Severity: Unknown
Chain: Ethereum (consensus layer)
Component: Lodestar
Published: 2021-12-01
Source: https://github.com/ChainSafe/js-libp2p-noise/issues/102
Type: ef-disclosure

## Details
Affected Clients: Lodestar
Uid: CL-2021-36
Bug: Improper nonce handling in Noise handshake
Type: BUG
Summary: There are two issues with nonce handling:<br><br>Nonces are 32 bits long. The Noise spec requires 64-bit nonce.<br><br>https://github.com/NodeFactoryIo/js-libp2p-noise/blob/master/src/%40types/handshake.d.ts#L12-L15<br><br>Nonce overflow.<br>The spec requires returning an error if the maximum number is reached. This is the same issue as in the flynn package but more realistic due to 32-bit length.<br><br>https://github.com/NodeFactoryIo/js-libp2p-noise/blob/master/src/handshakes/abstract-handshake.ts#L46-L48
Links: [https://github.com/ChainSafe/js-libp2p-noise/issues/102](https://github.com/ChainSafe/js-libp2p-noise/issues/102)
Reported: 2021-07-05
Published: 2021-12-01
Bounty Hunter: Taurus
Bounty Points: Part of EF initiated Security Audit: https://arxiv.org/abs/2109.11685
Bounty Reward (Usd): 0
