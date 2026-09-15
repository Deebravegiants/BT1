# [H] ALPINE-CVE-2016-1541

## Summary
Severity: High
Advisory: ALPINE-CVE-2016-1541
Ecosystem: Alpine:v3.4
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2016-05-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-1541
Type: osv

## Affected
- Alpine:v3.4: `libarchive` — affected >=0 <3.2.0-r0

## Details
Heap-based buffer overflow in the zip_read_mac_metadata function in archive_read_support_format_zip.c in libarchive before 3.2.0 allows remote attackers to execute arbitrary code via crafted entry-size values in a ZIP archive.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-1541
