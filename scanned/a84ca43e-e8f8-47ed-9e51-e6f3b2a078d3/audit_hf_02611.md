# [M] MemoryStateDB contains data race in DeleteState()

## Summary
Severity: Medium
Contest weight: 0.0929
Dataset id: 14028
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Upstream Optimism has two functions in op-chain-ops/state/memory_db.go that do not use the MemoryStateDB sync.RWMutex correctly. This was discovered when getting some background knowledge to aid in reviewing [DIFF] optimism/op-chain-ops. While this is outside of the scope of the Optimism diff it is worth mentioning here to make sure that it does not get left out of Blast for whatever reason. This could not be abused by an attacker but could cause instability when using the chain-ops utilities to modify the chain. Here is a PR with a fix.

## Recommendation
Either merge in the upstream change, merge in the single commit with the fix from the upstream PR via git cherry-pick, or make the same change to blast manually.
5.3
