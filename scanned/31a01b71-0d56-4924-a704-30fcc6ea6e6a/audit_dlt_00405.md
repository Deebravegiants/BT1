# [?] fix: avoid panic on partial chunk request for genesis chunk (#16141)

## Summary
Severity: Unknown
Chain: NEAR
Component: near/nearcore
Published: 2026-07-30
Source: https://github.com/near/nearcore/commit/556282637959c23a0bb50c33299fc55d542c6833
Type: security-commit

## Details
fix: avoid panic on partial chunk request for genesis chunk (#16141)

Any peer can ask for the genesis chunk by hash, and that used to panic
the node: the code asserts the receipts root it recomputes matches the
one in the chunk header, but genesis headers store an empty root.
Now return an error instead of asserting.
