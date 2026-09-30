# [H] ALPINE-CVE-2006-20001

## Summary
Severity: High
Advisory: ALPINE-CVE-2006-20001
Ecosystem: Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-01-17
Source: https://osv.dev/vulnerability/ALPINE-CVE-2006-20001
Type: osv

## Affected
- Alpine:v3.14: `apache2` — affected >=0 <2.4.55-r0
- Alpine:v3.15: `apache2` — affected >=0 <2.4.55-r0
- Alpine:v3.16: `apache2` — affected >=0 <2.4.55-r0
- Alpine:v3.17: `apache2` — affected >=0 <2.4.55-r0

## Details
A carefully crafted If: request header can cause a memory read, or write of a single zero byte, in a pool (heap) memory location beyond the header value sent. This could cause the process to crash.

This issue affects Apache HTTP Server 2.4.54 and earlier.

## References
- https://security.alpinelinux.org/vuln/CVE-2006-20001
