# [H] ALPINE-CVE-2019-19604

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-19604
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-12-11
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-19604
Type: osv

## Affected
- Alpine:v3.10: `git` — affected >=2.21.0 <2.22.2-r0
- Alpine:v3.11: `git` — affected >=2.21.0 <2.24.1-r0
- Alpine:v3.12: `git` — affected >=2.21.0 <2.24.1-r0
- Alpine:v3.13: `git` — affected >=2.21.0 <2.24.1-r0
- Alpine:v3.14: `git` — affected >=2.21.0 <2.24.1-r0
- Alpine:v3.15: `git` — affected >=2.21.0 <2.24.1-r0
- Alpine:v3.16: `git` — affected >=2.21.0 <2.24.1-r0
- Alpine:v3.17: `git` — affected >=2.21.0 <2.24.1-r0
- Alpine:v3.18: `git` — affected >=2.21.0 <2.24.1-r0
- Alpine:v3.19: `git` — affected >=2.21.0 <2.24.1-r0
- Alpine:v3.20: `git` — affected >=2.21.0 <2.24.1-r0
- Alpine:v3.21: `git` — affected >=2.21.0 <2.24.1-r0
- Alpine:v3.22: `git` — affected >=2.21.0 <2.24.1-r0
- Alpine:v3.23: `git` — affected >=2.21.0 <2.24.1-r0
- Alpine:v3.24: `git` — affected >=2.21.0 <2.24.1-r0

## Details
Arbitrary command execution is possible in Git before 2.20.2, 2.21.x before 2.21.1, 2.22.x before 2.22.2, 2.23.x before 2.23.1, and 2.24.x before 2.24.1 because a "git submodule update" operation can run commands found in the .gitmodules file of a malicious repository.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-19604
