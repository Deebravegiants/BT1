# [H] ALPINE-CVE-2016-9586

## Summary
Severity: High
Advisory: ALPINE-CVE-2016-9586
Ecosystem: Alpine:v3.2, Alpine:v3.3
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-04-23
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-9586
Type: osv

## Affected
- Alpine:v3.2: `curl` — affected >=0 <7.52.1-r0
- Alpine:v3.3: `curl` — affected >=0 <7.52.1-r0

## Details
curl before version 7.52.0 is vulnerable to a buffer overflow when doing a large floating point output in libcurl's implementation of the printf() functions. If there are any application that accepts a format string from the outside without necessary input filtering, it could allow remote attacks.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-9586
