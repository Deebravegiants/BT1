# [C] CVE-2019-25042

## Summary
Severity: Critical
Advisory: CVE-2019-25042
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-04-27
Source: https://osv.dev/vulnerability/CVE-2019-25042
Type: osv

## Details
Unbound before 1.9.5 allows an out-of-bounds write via a compressed name in rdata_copy. NOTE: The vendor disputes that this is a vulnerability. Although the code may be vulnerable, a running Unbound installation cannot be remotely or locally exploited

## References
- https://lists.debian.org/debian-lts-announce/2021/05/msg00007.html
- https://ostif.org/our-audit-of-unbound-dns-by-x41-d-sec-full-results/
- https://security.netapp.com/advisory/ntap-20210507-0007/
