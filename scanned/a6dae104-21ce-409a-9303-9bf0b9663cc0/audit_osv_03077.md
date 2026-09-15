# [M] ALPINE-CVE-2024-39312

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2024-39312
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2024-07-08
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-39312
Type: osv

## Affected
- Alpine:v3.17: `botan` — affected >=3.0.0 <2.19.5-r0
- Alpine:v3.18: `botan` — affected >=3.0.0 <2.19.5-r0
- Alpine:v3.19: `botan` — affected >=3.0.0 <2.19.5-r0
- Alpine:v3.20: `botan` — affected >=3.0.0 <2.19.5-r0
- Alpine:v3.21: `botan` — affected >=3.0.0 <2.19.5-r0
- Alpine:v3.21: `botan3` — affected >=0 <3.5.0-r0
- Alpine:v3.22: `botan3` — affected >=0 <3.5.0-r0
- Alpine:v3.23: `botan3` — affected >=0 <3.5.0-r0
- Alpine:v3.24: `botan3` — affected >=0 <3.5.0-r0

## Details
Botan is a C++ cryptography library. X.509 certificates can identify elliptic curves using either an object identifier or using explicit encoding of the parameters. A bug in the parsing of name constraint extensions in X.509 certificates meant that if the extension included both permitted subtrees and excluded subtrees, only the permitted subtree would be checked. If a certificate included a name which was permitted by the permitted subtree but also excluded by excluded subtree, it would be accepted. Fixed in versions 3.5.0 and 2.19.5.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-39312
