# [?] Merge pull request #7 from opentensor/security/ghsa-2026-003-owner-proxy-set-sn-owner-hotkey-alias-bypass

## Summary
Severity: Unknown
Chain: Bittensor
Component: opentensor/subtensor
Published: 2026-06-13
Source: https://github.com/RaoFoundation/subtensor/commit/5902428c50d4fe5ffe5f4df9a9e2f6ddb139cca1
Type: security-commit

## Details
Merge pull request #7 from opentensor/security/ghsa-2026-003-owner-proxy-set-sn-owner-hotkey-alias-bypass

Owner proxy `except sudo_set_sn_owner_hotkey` carve-out is bypassable via the duplicate alias `sudo_set_subnet_owner_hotkey`
