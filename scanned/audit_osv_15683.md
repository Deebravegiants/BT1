# [H] CVE-2019-18679

## Summary
Severity: High
Advisory: CVE-2019-18679
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-11-26
Source: https://osv.dev/vulnerability/CVE-2019-18679
Type: osv

## Details
An issue was discovered in Squid 2.x, 3.x, and 4.x through 4.8. Due to incorrect data management, it is vulnerable to information disclosure when processing HTTP Digest Authentication. Nonce tokens contain the raw byte value of a pointer that sits within heap memory allocation. This information reduces ASLR protections and may aid attackers isolating memory areas to target for remote code execution attacks.

## References
- https://lists.debian.org/debian-lts-announce/2020/07/msg00009.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/MTM74TU2BSLT5B3H4F3UDW53672NVLMC/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UEMOYTMCCFWK5NOXSXEIH5D2VGWVXR67/
- http://www.squid-cache.org/Advisories/SQUID-2019_11.txt
- http://www.squid-cache.org/Versions/v4/changesets/squid-4-671ba97abe929156dc4c717ee52ad22fba0f7443.patch
- https://lists.debian.org/debian-lts-announce/2019/12/msg00011.html
- https://security.gentoo.org/glsa/202003-34
- https://usn.ubuntu.com/4213-1/
- https://www.debian.org/security/2020/dsa-4682
- https://bugzilla.suse.com/show_bug.cgi?id=1156324
- https://github.com/squid-cache/squid/pull/491
