# [H] ALPINE-CVE-2019-20044

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-20044
Ecosystem: Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-02-24
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-20044
Type: osv

## Affected
- Alpine:v3.12: `zsh` — affected >=0 <5.8-r0
- Alpine:v3.13: `zsh` — affected >=0 <5.8-r0
- Alpine:v3.14: `zsh` — affected >=0 <5.8-r0
- Alpine:v3.15: `zsh` — affected >=0 <5.8-r0
- Alpine:v3.16: `zsh` — affected >=0 <5.8-r0
- Alpine:v3.17: `zsh` — affected >=0 <5.8-r0
- Alpine:v3.18: `zsh` — affected >=0 <5.8-r0
- Alpine:v3.19: `zsh` — affected >=0 <5.8-r0
- Alpine:v3.20: `zsh` — affected >=0 <5.8-r0
- Alpine:v3.21: `zsh` — affected >=0 <5.8-r0
- Alpine:v3.22: `zsh` — affected >=0 <5.8-r0
- Alpine:v3.23: `zsh` — affected >=0 <5.8-r0
- Alpine:v3.24: `zsh` — affected >=0 <5.8-r0

## Details
In Zsh before 5.8, attackers able to execute commands can regain privileges dropped by the --no-PRIVILEGED option. Zsh fails to overwrite the saved uid, so the original privileges can be restored by executing MODULE_PATH=/dir/with/module zmodload with a module that calls setuid().

## References
- https://security.alpinelinux.org/vuln/CVE-2019-20044
