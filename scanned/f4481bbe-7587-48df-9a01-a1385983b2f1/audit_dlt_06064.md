# [?] Fix republish RPC crash on non-send blocks when using the 'destinations' parameter and extend tests (#4972)

## Summary
Severity: Unknown
Chain: Nano
Component: nanocurrency/nano-node
Published: 2025-12-15
Source: https://github.com/nanocurrency/nano-node/commit/05de81c0331a81b2fdf79541c331ce2fda15aa11
Type: security-commit

## Details
Fix republish RPC crash on non-send blocks when using the 'destinations' parameter and extend tests (#4972)

The republish RPC previously called block_b->destination() unconditionally, which triggers a release_assert(false) when invoked on non-send blocks
