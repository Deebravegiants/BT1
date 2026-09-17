# [M] ALPINE-CVE-2015-8934

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2015-8934
Ecosystem: Alpine:v3.4
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2016-09-20
Source: https://osv.dev/vulnerability/ALPINE-CVE-2015-8934
Type: osv

## Affected
- Alpine:v3.4: `libarchive` — affected >=0 <3.2.1-r0

## Details
The copy_from_lzss_window function in archive_read_support_format_rar.c in libarchive 3.2.0 and earlier allows remote attackers to cause a denial of service (out-of-bounds heap read) via a crafted rar file.

## References
- https://security.alpinelinux.org/vuln/CVE-2015-8934
