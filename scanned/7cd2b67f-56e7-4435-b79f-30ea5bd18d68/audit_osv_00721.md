# [M] ALPINE-CVE-2017-7244

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2017-7244
Ecosystem: Alpine:v3.6
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-03-23
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-7244
Type: osv

## Affected
- Alpine:v3.6: `pcre` — affected >=0 <8.41-r0

## Details
The _pcre32_xclass function in pcre_xclass.c in libpcre1 in PCRE 8.40 allows remote attackers to cause a denial of service (invalid memory read) via a crafted file.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-7244
