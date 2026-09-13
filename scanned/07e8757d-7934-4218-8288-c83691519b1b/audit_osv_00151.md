# [H] ALPINE-CVE-2016-6250

## Summary
Severity: High
Advisory: ALPINE-CVE-2016-6250
Ecosystem: Alpine:v3.4
CVSS: 8.6 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:H)
Published: 2016-09-21
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-6250
Type: osv

## Affected
- Alpine:v3.4: `libarchive` — affected >=0 <3.2.1-r0

## Details
Integer overflow in the ISO9660 writer in libarchive before 3.2.1 allows remote attackers to cause a denial of service (application crash) or execute arbitrary code via vectors related to verifying filename lengths when writing an ISO9660 archive, which trigger a buffer overflow.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-6250
