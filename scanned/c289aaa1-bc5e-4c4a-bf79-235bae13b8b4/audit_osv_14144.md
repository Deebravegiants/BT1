# [C] CVE-2018-7442

## Summary
Severity: Critical
Advisory: CVE-2018-7442
CVSS: 9.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2018-02-23
Source: https://osv.dev/vulnerability/CVE-2018-7442
Type: osv

## Details
An issue was discovered in Leptonica through 1.75.3. The gplotMakeOutput function does not block '/' characters in the gplot rootname argument, potentially leading to path traversal and arbitrary file overwrite.

## References
- https://lists.debian.org/debian-lts/2018/02/msg00086.html
- https://security.gentoo.org/glsa/202312-01
