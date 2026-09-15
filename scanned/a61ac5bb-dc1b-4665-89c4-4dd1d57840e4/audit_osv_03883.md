# [C] ALPINE-CVE-2026-60002

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2026-60002
Ecosystem: Alpine:v3.24
CVSS: 9.4 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:L)
Published: 2026-07-08
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-60002
Type: osv

## Affected
- Alpine:v3.24: `openssh` — affected >=0 <10.3_p1-r1

## Details
ssh in OpenSSH before 10.4 can have a use-after-free when a server changes its host key during a key re-exchange. (This outcome occurs only on the client side.)

## References
- https://security.alpinelinux.org/vuln/CVE-2026-60002
