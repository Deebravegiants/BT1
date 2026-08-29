# [?] Merge pull request #6 from opentensor/security/ghsa-2026-002-swap-hotkey-v2-proxy-gap

## Summary
Severity: Unknown
Chain: Bittensor
Component: opentensor/subtensor
Published: 2026-06-13
Source: https://github.com/RaoFoundation/subtensor/commit/c52dac0ff96f5aee41a51a0b16d44f741d8ca12c
Type: security-commit

## Details
Merge pull request #6 from opentensor/security/ghsa-2026-002-swap-hotkey-v2-proxy-gap

NonFungible proxy denylist omits live `swap_hotkey_v2` (call 72), letting a scoped delegate reassign a victim's hotkey identity
