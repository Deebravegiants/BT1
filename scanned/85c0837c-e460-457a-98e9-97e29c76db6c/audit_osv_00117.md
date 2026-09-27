# [H] ALPINE-CVE-2016-4809

## Summary
Severity: High
Advisory: ALPINE-CVE-2016-4809
Ecosystem: Alpine:v3.4
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-09-21
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-4809
Type: osv

## Affected
- Alpine:v3.4: `libarchive` — affected >=0 <3.2.1-r0

## Details
The archive_read_format_cpio_read_header function in archive_read_support_format_cpio.c in libarchive before 3.2.1 allows remote attackers to cause a denial of service (application crash) via a CPIO archive with a large symlink.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-4809
