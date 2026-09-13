# [C] ALPINE-CVE-2016-7414

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2016-7414
Ecosystem: Alpine:v3.2, Alpine:v3.3
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-09-17
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-7414
Type: osv

## Affected
- Alpine:v3.2: `php` — affected >=0 <5.6.27-r0
- Alpine:v3.3: `php` — affected >=0 <5.6.27-r0

## Details
The ZIP signature-verification feature in PHP before 5.6.26 and 7.x before 7.0.11 does not ensure that the uncompressed_filesize field is large enough, which allows remote attackers to cause a denial of service (out-of-bounds memory access) or possibly have unspecified other impact via a crafted PHAR archive, related to ext/phar/util.c and ext/phar/zip.c.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-7414
