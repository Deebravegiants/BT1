# [H] ALPINE-CVE-2024-32004

## Summary
Severity: High
Advisory: ALPINE-CVE-2024-32004
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-05-14
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-32004
Type: osv

## Affected
- Alpine:v3.17: `git` — affected >=2.40.0 <2.39.5-r0
- Alpine:v3.18: `git` — affected >=2.40.0 <2.40.3-r0
- Alpine:v3.19: `git` — affected >=2.40.0 <2.43.4-r0
- Alpine:v3.20: `git` — affected >=2.40.0 <2.45.1-r0
- Alpine:v3.21: `git` — affected >=2.40.0 <2.45.1-r0
- Alpine:v3.22: `git` — affected >=2.40.0 <2.45.1-r0
- Alpine:v3.23: `git` — affected >=2.40.0 <2.45.1-r0
- Alpine:v3.24: `git` — affected >=2.40.0 <2.45.1-r0

## Details
Git is a revision control system. Prior to versions 2.45.1, 2.44.1, 2.43.4, 2.42.2, 2.41.1, 2.40.2, and 2.39.4, an attacker can prepare a local repository in such a way that, when cloned, will execute arbitrary code during the operation. The problem has been patched in versions 2.45.1, 2.44.1, 2.43.4, 2.42.2, 2.41.1, 2.40.2, and 2.39.4. As a workaround, avoid cloning repositories from untrusted sources.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-32004
