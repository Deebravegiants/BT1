# [H] ALPINE-CVE-2016-4302

## Summary
Severity: High
Advisory: ALPINE-CVE-2016-4302
Ecosystem: Alpine:v3.4
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2016-09-21
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-4302
Type: osv

## Affected
- Alpine:v3.4: `libarchive` — affected >=0 <3.2.1-r0

## Details
Heap-based buffer overflow in the parse_codes function in archive_read_support_format_rar.c in libarchive before 3.2.1 allows remote attackers to execute arbitrary code via a RAR file with a zero-sized dictionary.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-4302
