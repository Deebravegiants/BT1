# [H] CVE-2021-38714

## Summary
Severity: High
Advisory: CVE-2021-38714
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-08-24
Source: https://osv.dev/vulnerability/CVE-2021-38714
Type: osv

## Details
In Plib through 1.85, there is an integer overflow vulnerability that could result in arbitrary code execution. The vulnerability is found in ssgLoadTGA() function in src/ssg/ssgLoadTGA.cxx file.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/7HT3BKNAXLDY246UPUNRSBPGGVANRDOU/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/OTVSAKNCEYVMVAURQSB5GNA2MWL4XDPH/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/U5SML6W6Z2B6THT76VPUKUFYQJABODFU/
- https://lists.debian.org/debian-lts-announce/2021/10/msg00000.html
- https://sourceforge.net/p/plib/bugs/55/
