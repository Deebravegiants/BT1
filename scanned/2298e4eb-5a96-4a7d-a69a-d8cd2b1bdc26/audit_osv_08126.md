# [M] CVE-2016-10505

## Summary
Severity: Medium
Advisory: CVE-2016-10505
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-08-30
Source: https://osv.dev/vulnerability/CVE-2016-10505
Type: osv

## Details
NULL pointer dereference vulnerabilities in the imagetopnm function in convert.c, sycc444_to_rgb function in color.c, color_esycc_to_rgb function in color.c, and sycc422_to_rgb function in color.c in OpenJPEG before 2.2.0 allow remote attackers to cause a denial of service (application crash) via crafted j2k files.

## References
- https://security.gentoo.org/glsa/201710-26
- https://github.com/uclouvain/openjpeg/issues/776
- https://github.com/uclouvain/openjpeg/issues/784
- https://github.com/uclouvain/openjpeg/issues/785
- https://github.com/uclouvain/openjpeg/issues/792
