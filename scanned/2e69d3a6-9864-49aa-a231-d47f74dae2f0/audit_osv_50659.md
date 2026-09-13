# [M] CVE-2020-27350

## Summary
Severity: Medium
Advisory: CVE-2020-27350
CVSS: 5.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:L/I:L/A:L)
Published: 2020-12-10
Source: https://osv.dev/vulnerability/CVE-2020-27350
Type: osv

## Details
APT had several integer overflows and underflows while parsing .deb packages, aka GHSL-2020-168 GHSL-2020-169, in files apt-pkg/contrib/extracttar.cc, apt-pkg/deb/debfile.cc, and apt-pkg/contrib/arfile.cc. This issue affects: apt 1.2.32ubuntu0 versions prior to 1.2.32ubuntu0.2; 1.6.12ubuntu0 versions prior to 1.6.12ubuntu0.2; 2.0.2ubuntu0 versions prior to 2.0.2ubuntu0.2; 2.1.10ubuntu0 versions prior to 2.1.10ubuntu0.1;

## References
- https://bugs.launchpad.net/bugs/1899193
- https://usn.ubuntu.com/usn/usn-4667-1
- https://www.debian.org/security/2020/dsa-4808
- https://security.netapp.com/advisory/ntap-20210108-0005/
