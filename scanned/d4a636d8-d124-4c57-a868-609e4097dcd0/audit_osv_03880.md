# [M] ALPINE-CVE-2026-59998

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-59998
Ecosystem: Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-07-08
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-59998
Type: osv

## Affected
- Alpine:v3.24: `openssh` — affected >=0 <10.3_p1-r1

## Details
sshd in OpenSSH before 10.4 has an undocumented security-relevant behavior: GSSAPIStrictAcceptorCheck has no value if the server is in Windows Active Directory.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-59998
