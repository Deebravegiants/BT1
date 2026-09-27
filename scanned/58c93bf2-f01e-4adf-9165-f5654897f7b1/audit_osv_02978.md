# [H] ALPINE-CVE-2024-12088

## Summary
Severity: High
Advisory: ALPINE-CVE-2024-12088
Ecosystem: Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2025-01-14
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-12088
Type: osv

## Affected
- Alpine:v3.18: `rsync` — affected >=0 <3.4.0-r0
- Alpine:v3.19: `rsync` — affected >=0 <3.4.0-r0
- Alpine:v3.20: `rsync` — affected >=0 <3.4.0-r0
- Alpine:v3.21: `rsync` — affected >=0 <3.4.0-r0
- Alpine:v3.22: `rsync` — affected >=0 <3.4.0-r0
- Alpine:v3.23: `rsync` — affected >=0 <3.4.0-r0
- Alpine:v3.24: `rsync` — affected >=0 <3.4.0-r0

## Details
A flaw was found in rsync. When using the `--safe-links` option, the rsync client fails to properly verify if a symbolic link destination sent from the server contains another symbolic link within it. This results in a path traversal vulnerability, which may lead to arbitrary file write outside the desired directory.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-12088
