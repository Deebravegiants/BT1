# [H] CVE-2019-25041

## Summary
Severity: High
Advisory: CVE-2019-25041
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-04-27
Source: https://osv.dev/vulnerability/CVE-2019-25041
Type: osv

## Details
Unbound before 1.9.5 allows an assertion failure via a compressed name in dname_pkt_copy. NOTE: The vendor disputes that this is a vulnerability. Although the code may be vulnerable, a running Unbound installation cannot be remotely or locally exploited

## References
- https://lists.debian.org/debian-lts-announce/2021/05/msg00007.html
- https://security.netapp.com/advisory/ntap-20210507-0007/
- https://ostif.org/our-audit-of-unbound-dns-by-x41-d-sec-full-results/
