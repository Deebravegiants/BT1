# [M] ALPINE-CVE-2026-59995

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-59995
Ecosystem: Alpine:v3.24
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:L)
Published: 2026-07-08
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-59995
Type: osv

## Affected
- Alpine:v3.24: `openssh` — affected >=0 <10.3_p1-r1

## Details
sftp in OpenSSH before 10.4 does not properly constrain the location of downloaded files when "sftp server:/path ." is used with an attacker-controlled server.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-59995
