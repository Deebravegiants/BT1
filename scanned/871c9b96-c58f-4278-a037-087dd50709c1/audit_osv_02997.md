# [M] ALPINE-CVE-2024-22365

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2024-22365
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-06
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-22365
Type: osv

## Affected
- Alpine:v3.20: `linux-pam` — affected >=0 <1.6.0-r0
- Alpine:v3.21: `linux-pam` — affected >=0 <1.6.0-r0
- Alpine:v3.22: `linux-pam` — affected >=0 <1.6.0-r0
- Alpine:v3.23: `linux-pam` — affected >=0 <1.6.0-r0
- Alpine:v3.24: `linux-pam` — affected >=0 <1.6.0-r0

## Details
linux-pam (aka Linux PAM) before 1.6.0 allows attackers to cause a denial of service (blocked login process) via mkfifo because the openat call (for protect_dir) lacks O_DIRECTORY.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-22365
