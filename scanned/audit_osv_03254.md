# [H] ALPINE-CVE-2025-29087

## Summary
Severity: High
Advisory: ALPINE-CVE-2025-29087
Ecosystem: Alpine:v3.19, Alpine:v3.20, Alpine:v3.21
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-04-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-29087
Type: osv

## Affected
- Alpine:v3.19: `sqlite` — affected >=3.44.0 <3.44.2-r1
- Alpine:v3.20: `sqlite` — affected >=3.44.0 <3.45.3-r2
- Alpine:v3.21: `sqlite` — affected >=3.44.0 <3.48.0-r1

## Details
In SQLite 3.44.0 through 3.49.0 before 3.49.1, the concat_ws() SQL function can cause memory to be written beyond the end of a malloc-allocated buffer. If the separator argument is attacker-controlled and has a large string (e.g., 2MB or more), an integer overflow occurs in calculating the size of the result buffer, and thus malloc may not allocate enough memory.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-29087
