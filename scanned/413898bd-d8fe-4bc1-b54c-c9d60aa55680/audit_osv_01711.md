# [M] ALPINE-CVE-2020-10933

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-10933
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.8, Alpine:v3.9
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2020-05-04
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-10933
Type: osv

## Affected
- Alpine:v3.10: `ruby` — affected >=2.5.0 <2.5.8-r0
- Alpine:v3.11: `ruby` — affected >=2.5.0 <2.6.6-r0
- Alpine:v3.12: `ruby` — affected >=2.5.0 <2.6.6-r0
- Alpine:v3.13: `ruby` — affected >=2.5.0 <2.6.6-r0
- Alpine:v3.14: `ruby` — affected >=2.5.0 <2.6.6-r0
- Alpine:v3.15: `ruby` — affected >=2.5.0 <2.6.6-r0
- Alpine:v3.16: `ruby` — affected >=2.5.0 <2.6.6-r0
- Alpine:v3.17: `ruby` — affected >=2.5.0 <2.6.6-r0
- Alpine:v3.18: `ruby` — affected >=2.5.0 <2.6.6-r0
- Alpine:v3.19: `ruby` — affected >=2.5.0 <2.6.6-r0
- Alpine:v3.20: `ruby` — affected >=2.5.0 <2.6.6-r0
- Alpine:v3.21: `ruby` — affected >=2.5.0 <2.6.6-r0
- Alpine:v3.22: `ruby` — affected >=2.5.0 <2.6.6-r0
- Alpine:v3.23: `ruby` — affected >=2.5.0 <2.6.6-r0
- Alpine:v3.24: `ruby` — affected >=2.5.0 <2.6.6-r0
- Alpine:v3.8: `ruby` — affected >=2.5.0 <2.5.8-r0
- Alpine:v3.9: `ruby` — affected >=2.5.0 <2.5.8-r0

## Details
An issue was discovered in Ruby 2.5.x through 2.5.7, 2.6.x through 2.6.5, and 2.7.0. If a victim calls BasicSocket#read_nonblock(requested_size, buffer, exception: false), the method resizes the buffer to fit the requested size, but no data is copied. Thus, the buffer string provides the previous value of the heap. This may expose possibly sensitive data from the interpreter.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-10933
