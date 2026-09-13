# [M] CVE-2018-16548

## Summary
Severity: Medium
Advisory: CVE-2018-16548
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-09-05
Source: https://osv.dev/vulnerability/CVE-2018-16548
Type: osv

## Details
An issue was discovered in ZZIPlib through 0.13.69. There is a memory leak triggered in the function __zzip_parse_root_directory in zip.c, which will lead to a denial of service attack.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00065.html
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00066.html
- https://lists.debian.org/debian-lts-announce/2020/06/msg00029.html
- https://access.redhat.com/errata/RHSA-2019:2196
- https://github.com/gdraheim/zziplib/issues/58
