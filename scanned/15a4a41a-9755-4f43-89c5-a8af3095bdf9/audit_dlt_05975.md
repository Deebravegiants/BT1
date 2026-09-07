# [?] Merge pull request #14 from opentensor/security/ghsa-2026-010-hotkey-swap-rootclaimed-watermark-inflation

## Summary
Severity: Unknown
Chain: Bittensor
Component: opentensor/subtensor
Published: 2026-06-13
Source: https://github.com/RaoFoundation/subtensor/commit/ec86e0f4aa7c2c3c99f3c3e8162872460e341db8
Type: security-commit

## Details
Merge pull request #14 from opentensor/security/ghsa-2026-010-hotkey-swap-rootclaimed-watermark-inflation

Root cleanliness gate omits RootClaimed, letting hotkey-swap merge inflate the claimed high-water mark and under-pay future root dividends
