# [?] GHSA-2026-011: drop child-side (ParentKeys) cooldown gating

## Summary
Severity: Unknown
Chain: Bittensor
Component: opentensor/subtensor
Published: 2026-06-16
Source: https://github.com/RaoFoundation/subtensor/commit/7543a925f54f0290bba89fe9ef6e4b9b3905a371
Type: security-commit

## Details
GHSA-2026-011: drop child-side (ParentKeys) cooldown gating

Per review: gate the all-subnets hotkey-swap cooldown on membership OR being a
parent (ChildKeys), but NOT on the child side (ParentKeys). A parent can add any
hotkey as its child without consent (do_set_children), so gating on ParentKeys
would let a third party impose swap-cooldowns on a victim's hotkey — a griefing
vector. The swap still migrates the child relationship; it is just not gated.
Test updated to assert a child-only subnet is not cooldown-stamped.
