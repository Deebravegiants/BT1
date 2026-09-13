# [M] CVE-2019-1010189

## Summary
Severity: Medium
Advisory: CVE-2019-1010189
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-07-24
Source: https://osv.dev/vulnerability/CVE-2019-1010189
Type: osv

## Details
mgetty prior to version 1.2.1 is affected by: Infinite Loop. The impact is: DoS, the program does never terminates. The component is: g3/g32pbm.c. The attack vector is: Local, the user should open a specially crafted file. The fixed version is: 1.2.1.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YH7KTF6IB4LZURQHCOICNVE6YDAIHV62/
- https://www.x41-dsec.de/lab/advisories/x41-2018-007-mgetty/
