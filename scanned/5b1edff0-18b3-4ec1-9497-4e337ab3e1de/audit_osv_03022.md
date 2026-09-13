# [C] ALPINE-CVE-2024-27280

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2024-27280
Ecosystem: Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-14
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-27280
Type: osv

## Affected
- Alpine:v3.16: `ruby` — affected >=0 <3.1.5-r0
- Alpine:v3.17: `ruby` — affected >=0 <3.1.5-r0
- Alpine:v3.18: `ruby` — affected >=0 <3.2.4-r0
- Alpine:v3.19: `ruby` — affected >=0 <3.2.4-r0
- Alpine:v3.20: `ruby` — affected >=0 <3.3.1-r0
- Alpine:v3.21: `ruby` — affected >=0 <3.3.1-r0
- Alpine:v3.22: `ruby` — affected >=0 <3.3.1-r0
- Alpine:v3.23: `ruby` — affected >=0 <3.3.1-r0
- Alpine:v3.24: `ruby` — affected >=0 <3.3.1-r0

## Details
A buffer-overread issue was discovered in StringIO 3.0.1, as distributed in Ruby 3.0.x through 3.0.6 and 3.1.x through 3.1.4. The ungetbyte and ungetc methods on a StringIO can read past the end of a string, and a subsequent call to StringIO.gets may return the memory value. 3.0.3 is the main fixed version; however, for Ruby 3.0 users, a fixed version is stringio 3.0.1.1, and for Ruby 3.1 users, a fixed version is stringio 3.0.1.2.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-27280
