# [C] CVE-2019-12525

## Summary
Severity: Critical
Advisory: CVE-2019-12525
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-07-11
Source: https://osv.dev/vulnerability/CVE-2019-12525
Type: osv

## Details
An issue was discovered in Squid 3.3.9 through 3.5.28 and 4.x through 4.7. When Squid is configured to use Digest authentication, it parses the header Proxy-Authorization. It searches for certain tokens such as domain, uri, and qop. Squid checks if this token's value starts with a quote and ends with one. If so, it performs a memcpy of its length minus 2. Squid never checks whether the value is just a single quote (which would satisfy its requirements), leading to a memcpy of its length minus 1.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/SPXN2CLAGN5QSQBTOV5IGVLDOQSRFNTZ/
- http://lists.opensuse.org/opensuse-security-announce/2019-11/msg00053.html
- http://lists.opensuse.org/opensuse-security-announce/2019-11/msg00056.html
- http://www.squid-cache.org/Versions/v4/changesets/
- https://lists.debian.org/debian-lts-announce/2019/07/msg00018.html
- https://lists.debian.org/debian-lts-announce/2020/07/msg00009.html
- https://seclists.org/bugtraq/2019/Aug/42
- https://usn.ubuntu.com/4065-1/
- https://usn.ubuntu.com/4065-2/
- https://www.debian.org/security/2019/dsa-4507
- http://www.squid-cache.org/Versions/v4/changesets/squid-4-7f73e9c5d17664b882ed32590e6af310c247f320.patch
- https://github.com/squid-cache/squid/commits/v4
