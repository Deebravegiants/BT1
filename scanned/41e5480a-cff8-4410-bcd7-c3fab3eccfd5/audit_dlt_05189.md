# [?] security: bump rustls-webpki to 0.103.13 (RUSTSEC-2026-0104)

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2026-04-22
Source: https://github.com/Conflux-Chain/conflux-rust/commit/246c23edb05a53e294d80d6d4d472954d1d9478e
Type: security-commit

## Details
security: bump rustls-webpki to 0.103.13 (RUSTSEC-2026-0104)

Reachable panic in CRL parsing via BorrowedCertRevocationList::from_der
(mishandled empty BIT STRING in onlySomeReasons of IssuingDistributionPoint).
We do not configure CRL verification, so the vulnerable path is not reached;
bump to the SemVer-compatible patch release to clear the advisory.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
