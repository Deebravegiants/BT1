# [H] CVE-2019-12527

## Summary
Severity: High
Advisory: CVE-2019-12527
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-07-11
Source: https://osv.dev/vulnerability/CVE-2019-12527
Type: osv

## Details
An issue was discovered in Squid 4.0.23 through 4.7. When checking Basic Authentication with HttpHeader::getAuth, Squid uses a global buffer to store the decoded data. Squid does not check that the decoded length isn't greater than the buffer, leading to a heap-based buffer overflow with user controlled data.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-11/msg00053.html
- http://lists.opensuse.org/opensuse-security-announce/2019-11/msg00056.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/SPXN2CLAGN5QSQBTOV5IGVLDOQSRFNTZ/
- http://www.securityfocus.com/bid/109143
- http://www.squid-cache.org/Versions/v4/changesets/
- https://access.redhat.com/errata/RHSA-2019:2593
- https://seclists.org/bugtraq/2019/Aug/42
- https://usn.ubuntu.com/4065-1/
- https://www.debian.org/security/2019/dsa-4507
- http://www.squid-cache.org/Versions/v4/changesets/squid-4-7f73e9c5d17664b882ed32590e6af310c247f320.patch
- https://github.com/squid-cache/squid/commits/v4
