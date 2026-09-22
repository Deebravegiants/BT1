# [H] ALPINE-CVE-2017-1000117

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-1000117
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-10-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-1000117
Type: osv

## Affected
- Alpine:v3.10: `git` — affected >=0 <2.14.1-r0
- Alpine:v3.11: `git` — affected >=0 <2.14.1-r0
- Alpine:v3.12: `git` — affected >=0 <2.14.1-r0
- Alpine:v3.13: `git` — affected >=0 <2.14.1-r0
- Alpine:v3.14: `git` — affected >=0 <2.14.1-r0
- Alpine:v3.15: `git` — affected >=0 <2.14.1-r0
- Alpine:v3.16: `git` — affected >=0 <2.14.1-r0
- Alpine:v3.17: `git` — affected >=0 <2.14.1-r0
- Alpine:v3.18: `git` — affected >=0 <2.14.1-r0
- Alpine:v3.19: `git` — affected >=0 <2.14.1-r0
- Alpine:v3.20: `git` — affected >=0 <2.14.1-r0
- Alpine:v3.21: `git` — affected >=0 <2.14.1-r0
- Alpine:v3.22: `git` — affected >=0 <2.14.1-r0
- Alpine:v3.23: `git` — affected >=0 <2.14.1-r0
- Alpine:v3.24: `git` — affected >=0 <2.14.1-r0
- Alpine:v3.3: `git` — affected >=0 <2.8.6-r0
- Alpine:v3.4: `git` — affected >=0 <2.8.6
- Alpine:v3.5: `git` — affected >=0 <2.11.3-r0
- Alpine:v3.6: `git` — affected >=0 <2.13.5
- Alpine:v3.7: `git` — affected >=0 <2.14.1-r0
- Alpine:v3.8: `git` — affected >=0 <2.14.1-r0
- Alpine:v3.9: `git` — affected >=0 <2.14.1-r0

## Details
A malicious third-party can give a crafted "ssh://..." URL to an unsuspecting victim, and an attempt to visit the URL can result in any program that exists on the victim's machine being executed. Such a URL could be placed in the .gitmodules file of a malicious project, and an unsuspecting victim could be tricked into running "git clone --recurse-submodules" to trigger the vulnerability.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-1000117
