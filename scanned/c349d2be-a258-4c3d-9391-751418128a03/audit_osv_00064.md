# [M] ALPINE-CVE-2016-10713

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2016-10713
Ecosystem: Alpine:v3.4, Alpine:v3.5, Alpine:v3.6
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-02-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-10713
Type: osv

## Affected
- Alpine:v3.4: `patch` — affected >=0 <2.7.5-r3
- Alpine:v3.5: `patch` — affected >=0 <2.7.5-r3
- Alpine:v3.6: `patch` — affected >=0 <2.7.5-r3

## Details
An issue was discovered in GNU patch before 2.7.6. Out-of-bounds access within pch_write_line() in pch.c can possibly lead to DoS via a crafted input file.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-10713
