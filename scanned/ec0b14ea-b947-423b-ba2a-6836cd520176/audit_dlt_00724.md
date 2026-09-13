# [?] doc: Prove that the Merkle mutation check is sufficient (CVE-2012-2459).

## Summary
Severity: Unknown
Chain: Zcash
Component: zcash/zcash
Published: 2026-04-12
Source: https://github.com/zcash/zcash/commit/8f69946f2eee3501cd8241d3e7e325b7bb53998b
Type: security-commit

## Details
doc: Prove that the Merkle mutation check is sufficient (CVE-2012-2459).

Replace the "all known ways" hedge with an informal proof by strong
induction that (root, mutated=false) uniquely determines the
transaction list, assuming no SHA-256d collisions.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
