# [H] ALPINE-CVE-2017-7246

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-7246
Ecosystem: Alpine:v3.6
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-03-23
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-7246
Type: osv

## Affected
- Alpine:v3.6: `pcre` — affected >=0 <8.41-r0

## Details
Stack-based buffer overflow in the pcre32_copy_substring function in pcre_get.c in libpcre1 in PCRE 8.40 allows remote attackers to cause a denial of service (WRITE of size 268) or possibly have unspecified other impact via a crafted file.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-7246
