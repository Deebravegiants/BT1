# [M] ALPINE-CVE-2024-12747

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2024-12747
Ecosystem: Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.6 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2025-01-14
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-12747
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
A flaw was found in rsync. This vulnerability arises from a race condition during rsync's handling of symbolic links. Rsync's default behavior when encountering symbolic links is to skip them. If an attacker replaced a regular file with a symbolic link at the right time, it was possible to bypass the default behavior and traverse symbolic links. Depending on the privileges of the rsync process, an attacker could leak sensitive information, potentially leading to privilege escalation.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-12747
