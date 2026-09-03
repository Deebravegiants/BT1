# [?] fix(merkle_tree): don't panic in `BlockOutputWithProofs::verify_proofs` (#1717)

## Summary
Severity: Unknown
Chain: zkSync
Component: matter-labs/zksync-era
Published: 2024-04-18
Source: https://github.com/matter-labs/zksync-era/commit/a44fac97e0b121c93fde2d3fe15f494128cb3b16
Type: security-commit

## Details
fix(merkle_tree): don't panic in `BlockOutputWithProofs::verify_proofs` (#1717)

## What ❔

don't panic in `BlockOutputWithProofs::verify_proofs` and rather return
a `Result`

## Why ❔

So `BlockOutputWithProofs::verify_proofs` can be used by other
components.

## Checklist

- [x] PR title corresponds to the body of PR (we generate changelog
entries from PRs).
- [x] Tests for the changes have been added / updated.
- [x] Documentation comments have been added / updated.
- [x] Code has been formatted via `zk fmt` and `zk lint`.
- [ ] Spellcheck has been run via `zk spellcheck`.
- [ ] Linkcheck has been run via `zk linkcheck`.

Signed-off-by: Harald Hoyer <harald@matterlabs.dev>
