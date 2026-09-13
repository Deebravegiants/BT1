# [H] ALPINE-CVE-2021-45444

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-45444
Ecosystem: Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-02-14
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-45444
Type: osv

## Affected
- Alpine:v3.12: `zsh` — affected >=0 <5.8.1-r0
- Alpine:v3.13: `zsh` — affected >=0 <5.8.1-r0
- Alpine:v3.14: `zsh` — affected >=0 <5.8.1-r0
- Alpine:v3.15: `zsh` — affected >=0 <5.8.1-r0
- Alpine:v3.16: `zsh` — affected >=0 <5.8.1-r0
- Alpine:v3.17: `zsh` — affected >=0 <5.8.1-r0
- Alpine:v3.18: `zsh` — affected >=0 <5.8.1-r0
- Alpine:v3.19: `zsh` — affected >=0 <5.8.1-r0
- Alpine:v3.20: `zsh` — affected >=0 <5.8.1-r0
- Alpine:v3.21: `zsh` — affected >=0 <5.8.1-r0
- Alpine:v3.22: `zsh` — affected >=0 <5.8.1-r0
- Alpine:v3.23: `zsh` — affected >=0 <5.8.1-r0
- Alpine:v3.24: `zsh` — affected >=0 <5.8.1-r0

## Details
In zsh before 5.8.1, an attacker can achieve code execution if they control a command output inside the prompt, as demonstrated by a %F argument. This occurs because of recursive PROMPT_SUBST expansion.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-45444
