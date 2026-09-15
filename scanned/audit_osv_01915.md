# [H] ALPINE-CVE-2020-27347

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-27347
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-11-06
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-27347
Type: osv

## Affected
- Alpine:v3.10: `tmux` — affected >=2.9 <2.9a-r2
- Alpine:v3.11: `tmux` — affected >=2.9 <3.0a-r2
- Alpine:v3.12: `tmux` — affected >=2.9 <3.1c-r0
- Alpine:v3.13: `tmux` — affected >=2.9 <3.1c-r0
- Alpine:v3.14: `tmux` — affected >=2.9 <3.1c-r0
- Alpine:v3.15: `tmux` — affected >=2.9 <3.1c-r0
- Alpine:v3.16: `tmux` — affected >=2.9 <3.1c-r0
- Alpine:v3.17: `tmux` — affected >=2.9 <3.1c-r0
- Alpine:v3.18: `tmux` — affected >=2.9 <3.1c-r0
- Alpine:v3.19: `tmux` — affected >=2.9 <3.1c-r0
- Alpine:v3.20: `tmux` — affected >=2.9 <3.1c-r0
- Alpine:v3.21: `tmux` — affected >=2.9 <3.1c-r0
- Alpine:v3.22: `tmux` — affected >=2.9 <3.1c-r0
- Alpine:v3.23: `tmux` — affected >=2.9 <3.1c-r0
- Alpine:v3.24: `tmux` — affected >=2.9 <3.1c-r0

## Details
In tmux before version 3.1c the function input_csi_dispatch_sgr_colon() in file input.c contained a stack-based buffer-overflow that can be exploited by terminal output.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-27347
