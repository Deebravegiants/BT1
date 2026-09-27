# [H] CVE-2021-22555

## Summary
Severity: High
Advisory: CVE-2021-22555
Aliases: A-184847809, PUB-A-184847809
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-07-07
Source: https://osv.dev/vulnerability/CVE-2021-22555
Type: osv

## Details
A heap out-of-bounds write affecting Linux since v2.6.19-rc1 was discovered in net/netfilter/x_tables.c. This allows an attacker to gain privileges or cause a DoS (via heap memory corruption) through user name space

## References
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2021-22555
- http://packetstormsecurity.com/files/163528/Linux-Kernel-Netfilter-Heap-Out-Of-Bounds-Write.html
- https://security.netapp.com/advisory/ntap-20210805-0010/
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/net/netfilter/x_tables.c?id=9fa492cdc160cd27ce1046cb36f47d3b2b1efa21
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/net/netfilter/x_tables.c?id=b29c457a6511435960115c0f548c4360d5f4801d
- http://packetstormsecurity.com/files/164155/Kernel-Live-Patch-Security-Notice-LSN-0081-1.html
- http://packetstormsecurity.com/files/164437/Netfilter-x_tables-Heap-Out-Of-Bounds-Write-Privilege-Escalation.html
- http://packetstormsecurity.com/files/165477/Kernel-Live-Patch-Security-Notice-LSN-0083-1.html
- https://github.com/google/security-research/security/advisories/GHSA-xxx5-8mvq-3528
- http://packetstormsecurity.com/files/163878/Kernel-Live-Patch-Security-Notice-LSN-0080-1.html
