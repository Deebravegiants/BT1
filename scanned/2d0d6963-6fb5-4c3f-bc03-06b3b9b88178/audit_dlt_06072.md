# [?] Summonerd: Correctly handle contribution handler crashes

## Summary
Severity: Unknown
Chain: Penumbra
Component: penumbra-zone/penumbra
Published: 2023-10-21
Source: https://github.com/penumbra-zone/penumbra/commit/8e215d745409627071e93c0052c180efd667c9c3
Type: security-commit

## Details
Summonerd: Correctly handle contribution handler crashes

Now we correctly bubble these upstream and crash the entire server.

This is what we want, because these crashes are unexpected and
indicative of some actual issue.
