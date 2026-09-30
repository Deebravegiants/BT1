# [M] ALPINE-CVE-2026-5222

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-5222
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-05-25
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-5222
Type: osv

## Affected
- Alpine:v3.23: `rust` — affected >=0 <1.91.1-r2
- Alpine:v3.24: `rust` — affected >=0 <1.96.0-r0

## Details
Cargo between 1.68 and 1.96 incorrectly normalized the URLs of third-party registries using the sparse index protocol. If a hosting provider allowed multiple registries to be hosted with arbitrary names within the same domain, an attacker able to publish crates in a registry could obtain the credentials of others users of the same registry. The severity of the vulnerability is **low**, due to the extremely niche requirements needed to achieve the attack.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-5222
