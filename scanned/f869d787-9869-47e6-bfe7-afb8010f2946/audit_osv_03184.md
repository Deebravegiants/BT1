# [M] ALPINE-CVE-2025-10966

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2025-10966
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2025-11-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-10966
Type: osv

## Affected
- Alpine:v3.23: `curl` — affected >=7.69.0 <8.17.0-r0
- Alpine:v3.24: `curl` — affected >=7.69.0 <8.17.0-r0

## Details
curl's code for managing SSH connections when SFTP was done using the wolfSSH
powered backend was flawed and missed host verification mechanisms.

This prevents curl from detecting MITM attackers and more.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-10966
