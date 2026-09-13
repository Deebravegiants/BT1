# [H] CVE-2019-12854

## Summary
Severity: High
Advisory: CVE-2019-12854
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-08-15
Source: https://osv.dev/vulnerability/CVE-2019-12854
Type: osv

## Details
Due to incorrect string termination, Squid cachemgr.cgi 4.0 through 4.7 may access unallocated memory. On systems with memory access protections, this can cause the CGI process to terminate unexpectedly, resulting in a denial of service for all clients using it.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/SPXN2CLAGN5QSQBTOV5IGVLDOQSRFNTZ/
- http://lists.opensuse.org/opensuse-security-announce/2019-11/msg00053.html
- http://lists.opensuse.org/opensuse-security-announce/2019-11/msg00056.html
- http://www.squid-cache.org/Advisories/SQUID-2019_1.txt
- https://bugs.squid-cache.org/show_bug.cgi?id=4937
- https://seclists.org/bugtraq/2019/Aug/42
- https://usn.ubuntu.com/4213-1/
- https://www.debian.org/security/2019/dsa-4507
- http://www.squid-cache.org/Versions/v4/changesets/squid-4-2981a957716c61ff7e21eee1d7d6eb5a237e466d.patch
