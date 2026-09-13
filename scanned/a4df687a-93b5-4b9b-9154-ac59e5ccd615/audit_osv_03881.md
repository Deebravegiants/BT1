# [H] ALPINE-CVE-2026-59999

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-59999
Ecosystem: Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-07-08
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-59999
Type: osv

## Affected
- Alpine:v3.24: `openssh` — affected >=0 <10.3_p1-r1

## Details
In sshd in OpenSSH before 10.4, DisableForwarding=yes was supposed to take precedence over PermitTunnel=yes, but did not.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-59999
