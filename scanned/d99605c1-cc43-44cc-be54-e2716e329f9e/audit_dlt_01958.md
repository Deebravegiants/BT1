# [?] ethereum: deploy test token nonce race condition fix

## Summary
Severity: Unknown
Chain: Wormhole
Component: wormhole-foundation/wormhole
Published: 2022-10-28
Source: https://github.com/wormhole-foundation/wormhole/commit/25d2f24b03a0fa29629fe8fbb3a2c918fb49834b
Type: security-commit

## Details
ethereum: deploy test token nonce race condition fix

Noticed this error happening in tilt sometimes:

[tests] Error: Returned error: VM Exception while processing transaction: the tx
doesn't have the correct nonce. account has nonce of: 17 tx has nonce of: 16

It's not safe to submit txs in parallel, because the nonce can get out of sync.
Instead we should submit them serially.
