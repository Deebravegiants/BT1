# [H] ALPINE-CVE-2022-27778

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-27778
Ecosystem: Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:H)
Published: 2022-06-02
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-27778
Type: osv

## Affected
- Alpine:v3.16: `curl` — affected >=0 <7.83.1-r0
- Alpine:v3.17: `curl` — affected >=0 <7.83.1-r0
- Alpine:v3.18: `curl` — affected >=0 <7.83.1-r0
- Alpine:v3.19: `curl` — affected >=0 <7.83.1-r0
- Alpine:v3.20: `curl` — affected >=0 <7.83.1-r0
- Alpine:v3.21: `curl` — affected >=0 <7.83.1-r0
- Alpine:v3.22: `curl` — affected >=0 <7.83.1-r0
- Alpine:v3.23: `curl` — affected >=0 <7.83.1-r0
- Alpine:v3.24: `curl` — affected >=0 <7.83.1-r0

## Details
A use of incorrectly resolved name vulnerability fixed in 7.83.1 might remove the wrong file when `--no-clobber` is used together with `--remove-on-error`.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-27778
