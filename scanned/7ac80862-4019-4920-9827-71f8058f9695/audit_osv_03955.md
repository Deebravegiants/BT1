# [M] ALPINE-CVE-2026-73282

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-73282
Ecosystem: Alpine:v3.24
CVSS: 4.8 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-73282
Type: osv

## Affected
- Alpine:v3.24: `openssh` — affected >=0 <10.3_p1-r1

## Details
In ssh in OpenSSH before 10.5, a use-after-free for realloc data can occur if a certain pair of remote-forwarding operations are concurrent.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-73282
