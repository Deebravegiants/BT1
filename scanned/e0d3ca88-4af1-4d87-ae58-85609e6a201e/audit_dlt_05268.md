# [?] crypto/secp256k1: add test for CVE-2026-26315 coordinate validation

## Summary
Severity: Unknown
Chain: Ethereum Classic
Component: etclabscore/core-geth
Published: 2026-03-27
Source: https://github.com/etclabscore/core-geth/commit/46bba8dfc89e1457a0fb82fc6583305399ba76f4
Type: security-commit

## Details
crypto/secp256k1: add test for CVE-2026-26315 coordinate validation

Test verifies that IsOnCurve rejects points with coordinates >= P.
Without the fix in the next commit, this test fails because coordinates
equivalent mod P (e.g. Gx+P) are incorrectly accepted as valid.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
