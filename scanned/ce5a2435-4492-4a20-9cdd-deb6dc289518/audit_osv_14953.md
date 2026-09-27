# [M] CVE-2019-12529

## Summary
Severity: Medium
Advisory: CVE-2019-12529
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-07-11
Source: https://osv.dev/vulnerability/CVE-2019-12529
Type: osv

## Details
An issue was discovered in Squid 2.x through 2.7.STABLE9, 3.x through 3.5.28, and 4.x through 4.7. When Squid is configured to use Basic Authentication, the Proxy-Authorization header is parsed via uudecode. uudecode determines how many bytes will be decoded by iterating over the input and checking its table. The length is then used to start decoding the string. There are no checks to ensure that the length it calculates isn't greater than the input buffer. This leads to adjacent memory being decoded as well. An attacker would not be able to retrieve the decoded data unless the Squid maintainer had configured the display of usernames on error pages.

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
- http://www.squid-cache.org/Versions/v4/changesets/squid-4-dd46b5417809647f561d8a5e0e74c3aacd235258.patch
- https://github.com/squid-cache/squid/commits/v4
