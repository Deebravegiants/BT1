# [H] rPGP affected by crash in message handling for deeply nested messages

## Summary
Severity: High
Advisory: GHSA-8h58-w33p-wq3g
CWE: CWE-121
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-02-13
Source: https://github.com/advisories/GHSA-8h58-w33p-wq3g
Type: github-advisory

## Affected
- crates.io: `pgp` — affected >=0.16.0-alpha.0 <0.19.0

## Details
### Summary
Previous rPGP versions could be caused to crash with a "stack overflow" when parsing messages that contain deeply nested message layers, such as messages with many signatures.

rPGP 0.19.0 resolves this issue with a more robust message handling implementation (via https://github.com/rpgp/rpgp/pull/625).

### Impact
An attacker could cause applications to crash in rPGP's message parsing subsystem, when applications attempt to ingest messages.

### Attribution
Discovered internally during rPGP development, using a fuzz test suite previously contributed by Christian Reitter.

## References
- https://github.com/rpgp/rpgp/security/advisories/GHSA-8h58-w33p-wq3g
- https://github.com/rpgp/rpgp/pull/625
- https://github.com/rpgp/rpgp/commit/e82f2c7494ba277d62fd372d69b2c008473bbef8
- https://github.com/rpgp/rpgp
