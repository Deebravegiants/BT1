# [M] CVE-2020-27842

## Summary
Severity: Medium
Advisory: CVE-2020-27842
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-01-05
Source: https://osv.dev/vulnerability/CVE-2020-27842
Type: osv

## Details
There's a flaw in openjpeg's t2 encoder in versions prior to 2.4.0. An attacker who is able to provide crafted input to be processed by openjpeg could cause a null pointer dereference. The highest impact of this flaw is to application availability.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WJUPGIZE6A4O52EBOF75MCXJOL6MUCRV/
- https://lists.debian.org/debian-lts-announce/2022/04/msg00006.html
- https://security.gentoo.org/glsa/202101-29
- https://www.debian.org/security/2021/dsa-4882
- https://bugzilla.redhat.com/show_bug.cgi?id=1907513
- https://www.oracle.com//security-alerts/cpujul2021.html
- https://www.oracle.com/security-alerts/cpuApr2021.html
