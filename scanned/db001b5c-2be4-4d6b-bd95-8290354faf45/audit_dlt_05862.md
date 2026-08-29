# [?] chore(rust): patch RUSTSEC-2026-0104 in rustls-webpki (#20235)

## Summary
Severity: Unknown
Chain: Optimism
Component: ethereum-optimism/optimism
Published: 2026-04-22
Source: https://github.com/ethereum-optimism/optimism/commit/b2119af4daa3a44206a72cfdf240f49e33ea5ed5
Type: security-commit

## Details
chore(rust): patch RUSTSEC-2026-0104 in rustls-webpki (#20235)

Bump rustls-webpki 0.103.12 -> 0.103.13 to fix a reachable panic when
parsing certificate revocation lists. Also drop the stale
RUSTSEC-2026-0097 ignore entry, which no longer matches any crate.

Co-authored-by: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
