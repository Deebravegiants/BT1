# [?] Allow user provided signature set accounts to prevent DoS

## Summary
Severity: Unknown
Chain: Wormhole
Component: wormhole-foundation/wormhole
Published: 2021-07-26
Source: https://github.com/wormhole-foundation/wormhole/commit/42c3040de1a9faf3f1957e23f56d075cbe2c0347
Type: security-commit

## Details
Allow user provided signature set accounts to prevent DoS

With derived signature set accounts, an old guardian set could frontrun the creation of the account. Since the hash is persisted in the account, we don't need to encode it in the account address.

Change-Id: I49ca46611eb587c8234ac9b2c459263a2ace4219
