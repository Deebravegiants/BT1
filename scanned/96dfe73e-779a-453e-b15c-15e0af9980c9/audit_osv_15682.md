# [M] CVE-2019-18678

## Summary
Severity: Medium
Advisory: CVE-2019-18678
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2019-11-26
Source: https://osv.dev/vulnerability/CVE-2019-18678
Type: osv

## Details
An issue was discovered in Squid 3.x and 4.x through 4.8. It allows attackers to smuggle HTTP requests through frontend software to a Squid instance that splits the HTTP Request pipeline differently. The resulting Response messages corrupt caches (between a client and Squid) with attacker-controlled content at arbitrary URLs. Effects are isolated to software between the attacker client and Squid. There are no effects on Squid itself, nor on any upstream servers. The issue is related to a request header containing whitespace between a header name and a colon.

## References
- https://lists.debian.org/debian-lts-announce/2020/07/msg00009.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/MTM74TU2BSLT5B3H4F3UDW53672NVLMC/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UEMOYTMCCFWK5NOXSXEIH5D2VGWVXR67/
- http://www.squid-cache.org/Advisories/SQUID-2019_10.txt
- http://www.squid-cache.org/Versions/v4/changesets/squid-4-671ba97abe929156dc4c717ee52ad22fba0f7443.patch
- https://lists.debian.org/debian-lts-announce/2019/12/msg00011.html
- https://security.gentoo.org/glsa/202003-34
- https://usn.ubuntu.com/4213-1/
- https://www.debian.org/security/2020/dsa-4682
- https://bugzilla.suse.com/show_bug.cgi?id=1156323
- https://github.com/squid-cache/squid/pull/445
