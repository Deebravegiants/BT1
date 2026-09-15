# [C] CVE-2018-7440

## Summary
Severity: Critical
Advisory: CVE-2018-7440
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-02-23
Source: https://osv.dev/vulnerability/CVE-2018-7440
Type: osv

## Details
An issue was discovered in Leptonica through 1.75.3. The gplotMakeOutput function allows command injection via a $(command) approach in the gplot rootname argument. This issue exists because of an incomplete fix for CVE-2018-3836.

## References
- https://github.com/DanBloomberg/leptonica/issues/303#issuecomment-366472212
- https://lists.debian.org/debian-lts-announce/2018/03/msg00005.html
- https://security.gentoo.org/glsa/202312-01
