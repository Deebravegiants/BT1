# [M] ALPINE-CVE-2018-14851

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-14851
Ecosystem: Alpine:v3.5
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-08-02
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-14851
Type: osv

## Affected
- Alpine:v3.5: `php5` — affected >=0 <5.6.37-r0

## Details
exif_process_IFD_in_MAKERNOTE in ext/exif/exif.c in PHP before 5.6.37, 7.0.x before 7.0.31, 7.1.x before 7.1.20, and 7.2.x before 7.2.8 allows remote attackers to cause a denial of service (out-of-bounds read and application crash) via a crafted JPEG file.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-14851
