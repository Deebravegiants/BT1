# [H] CVE-2020-29361

## Summary
Severity: High
Advisory: CVE-2020-29361
Aliases: GHSA-q4r3-hm6m-mvc2
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-12-16
Source: https://osv.dev/vulnerability/CVE-2020-29361
Type: osv

## Details
An issue was discovered in p11-kit 0.21.1 through 0.23.21. Multiple integer overflows have been discovered in the array allocations in the p11-kit library and the p11-kit list command, where overflow checks are missing before calling realloc or calloc.

## References
- https://lists.apache.org/thread.html/r58af02e294bd07f487e2c64ffc0a29b837db5600e33b6e698b9d696b%40%3Cissues.bookkeeper.apache.org%3E
- https://lists.apache.org/thread.html/rf4c02775860db415b4955778a131c2795223f61cb8c6a450893651e4%40%3Cissues.bookkeeper.apache.org%3E
- https://github.com/p11-glue/p11-kit/releases
- https://github.com/p11-glue/p11-kit/security/advisories/GHSA-q4r3-hm6m-mvc2
- https://lists.debian.org/debian-lts-announce/2021/01/msg00002.html
- https://www.debian.org/security/2021/dsa-4822
