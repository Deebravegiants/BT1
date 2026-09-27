# [H] CVE-2020-27814

## Summary
Severity: High
Advisory: CVE-2020-27814
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-01-26
Source: https://osv.dev/vulnerability/CVE-2020-27814
Type: osv

## Details
A heap-buffer overflow was found in the way openjpeg2 handled certain PNG format files. An attacker could use this flaw to cause an application crash or in some cases execute arbitrary code with the permission of the user running such an application.

## References
- https://lists.debian.org/debian-lts-announce/2021/02/msg00011.html
- https://security.gentoo.org/glsa/202101-29
- https://www.debian.org/security/2021/dsa-4882
- https://www.oracle.com//security-alerts/cpujul2021.html
- https://github.com/uclouvain/openjpeg/issues/1283
- https://bugzilla.redhat.com/show_bug.cgi?id=1901998
