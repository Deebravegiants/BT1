# [C] ALPINE-CVE-2018-11219

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2018-11219
Ecosystem: Alpine:v3.5, Alpine:v3.6, Alpine:v3.7
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-06-17
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-11219
Type: osv

## Affected
- Alpine:v3.5: `redis` — affected >=4.0 <3.2.12-r0
- Alpine:v3.6: `redis` — affected >=4.0 <3.2.12-r0
- Alpine:v3.7: `redis` — affected >=4.0 <4.0.10-r0

## Details
An Integer Overflow issue was discovered in the struct library in the Lua subsystem in Redis before 3.2.12, 4.x before 4.0.10, and 5.x before 5.0 RC2, leading to a failure of bounds checking.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-11219
