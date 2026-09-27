# [?] Merge pull request #18 from opentensor/security/ghsa-2026-014-childkey-take-not-migrated-on-hotkey-swap

## Summary
Severity: Unknown
Chain: Bittensor
Component: opentensor/subtensor
Published: 2026-06-13
Source: https://github.com/RaoFoundation/subtensor/commit/d0e9c43bf701a149b8ff04a0dc9e2da665846604
Type: security-commit

## Details
Merge pull request #18 from opentensor/security/ghsa-2026-014-childkey-take-not-migrated-on-hotkey-swap

Per-subnet ChildkeyTake is not migrated during hotkey swap, silently resetting the new hotkey's take to the subnet floor
