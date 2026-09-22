# [H] ALPINE-CVE-2026-60000

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-60000
Ecosystem: Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-08
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-60000
Type: osv

## Affected
- Alpine:v3.24: `openssh` — affected >=0 <10.3_p1-r1

## Details
sshd in OpenSSH before 10.4 allows remote attackers to cause a denial of service (resource consumption from excessive authentication attempts) because MaxAuthTries was mishandled for GSSAPIAuthentication.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-60000
