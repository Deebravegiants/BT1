# [M] 5.2.1 MemoryStateDBcontains data race inDeleteState()

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk

**Context:** op-chain-ops/state/memory_db.go

**Description:** Upstream Optimism has two functions inop-chain-ops/state/memory_db.gothat do not use the
MemoryStateDB sync.RWMutexcorrectly. This was discovered when getting some background knowledge to aid
in reviewing [DIFF] optimism/op-chain-ops. While this is outside of the scope of the Optimism diff it is worth
mentioning here to make sure that it does not get left out of Blast for whatever reason. This could not be abused
by an attacker but could cause instability when using the chain-ops utilities to modify the chain. Here is a PR with
a fix.

**Recommendation:** Either merge in the upstream change, merge in the single commit with the fix from the up-
stream PR viagit cherry-pick, or make the same change to blast manually.
