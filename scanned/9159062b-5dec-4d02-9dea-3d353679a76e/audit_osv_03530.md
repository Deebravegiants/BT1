# [H] ALPINE-CVE-2026-26740

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-26740
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H)
Published: 2026-03-18
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-26740
Type: osv

## Affected
- Alpine:v3.21: `giflib` — affected >=0 <5.2.2-r2
- Alpine:v3.22: `giflib` — affected >=0 <5.2.2-r2
- Alpine:v3.23: `giflib` — affected >=0 <5.2.2-r2
- Alpine:v3.24: `giflib` — affected >=0 <5.2.2-r2

## Details
Buffer Overflow vulnerability in giflib v.5.2.2 allows a remote attacker to cause a denial of service via the EGifGCBToExtension overwriting an existing Graphic Control Extension block without validating its allocated size.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-26740
