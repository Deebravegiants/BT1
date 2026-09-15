# [H] ALPINE-CVE-2016-4300

## Summary
Severity: High
Advisory: ALPINE-CVE-2016-4300
Ecosystem: Alpine:v3.4
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2016-09-21
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-4300
Type: osv

## Affected
- Alpine:v3.4: `libarchive` — affected >=0 <3.2.1-r0

## Details
Integer overflow in the read_SubStreamsInfo function in archive_read_support_format_7zip.c in libarchive before 3.2.1 allows remote attackers to execute arbitrary code via a 7zip file with a large number of substreams, which triggers a heap-based buffer overflow.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-4300
