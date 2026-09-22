# [H] ALPINE-CVE-2022-29187

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-29187
Ecosystem: Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-07-12
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-29187
Type: osv

## Affected
- Alpine:v3.13: `git` — affected >=2.30.3 <2.30.5-r0
- Alpine:v3.14: `git` — affected >=2.30.3 <2.32.3-r0
- Alpine:v3.15: `git` — affected >=2.30.3 <2.34.4-r0
- Alpine:v3.16: `git` — affected >=2.30.3 <2.36.2-r0
- Alpine:v3.17: `git` — affected >=2.30.3 <2.37.1-r0
- Alpine:v3.18: `git` — affected >=2.30.3 <2.37.1-r0
- Alpine:v3.19: `git` — affected >=2.30.3 <2.37.1-r0
- Alpine:v3.20: `git` — affected >=2.30.3 <2.37.1-r0
- Alpine:v3.21: `git` — affected >=2.30.3 <2.37.1-r0
- Alpine:v3.22: `git` — affected >=2.30.3 <2.37.1-r0
- Alpine:v3.23: `git` — affected >=2.30.3 <2.37.1-r0
- Alpine:v3.24: `git` — affected >=2.30.3 <2.37.1-r0

## Details
Git is a distributed revision control system. Git prior to versions 2.37.1, 2.36.2, 2.35.4, 2.34.4, 2.33.4, 2.32.3, 2.31.4, and 2.30.5, is vulnerable to privilege escalation in all platforms. An unsuspecting user could still be affected by the issue reported in CVE-2022-24765, for example when navigating as root into a shared tmp directory that is owned by them, but where an attacker could create a git repository. Versions 2.37.1, 2.36.2, 2.35.4, 2.34.4, 2.33.4, 2.32.3, 2.31.4, and 2.30.5 contain a patch for this issue. The simplest way to avoid being affected by the exploit described in the example is to avoid running git as root (or an Administrator in Windows), and if needed to reduce its use to a minimum. While a generic workaround is not possible, a system could be hardened from the exploit described in the example by removing any such repository if it exists already and creating one as root to block any future attacks.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-29187
