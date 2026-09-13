# [M] ALPINE-CVE-2026-59997

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-59997
Ecosystem: Alpine:v3.24
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N)
Published: 2026-07-08
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-59997
Type: osv

## Affected
- Alpine:v3.24: `openssh` — affected >=0 <10.3_p1-r1

## Details
internal-sftp in sshd in OpenSSH before 10.4 recognizes only the first 9 command-line arguments, which can be important if a later command-line argument would have helped to ensure the intended security properties of an SFTP connection.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-59997
