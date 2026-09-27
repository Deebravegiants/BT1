# [H] CVE-2019-12520

## Summary
Severity: High
Advisory: CVE-2019-12520
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-04-15
Source: https://osv.dev/vulnerability/CVE-2019-12520
Type: osv

## Details
An issue was discovered in Squid through 4.7 and 5. When receiving a request, Squid checks its cache to see if it can serve up a response. It does this by making a MD5 hash of the absolute URL of the request. If found, it servers the request. The absolute URL can include the decoded UserInfo (username and password) for certain protocols. This decoded info is prepended to the domain. This allows an attacker to provide a username that has special characters to delimit the domain, and treat the rest of the URL as a path or query string. An attacker could first make a request to their domain using an encoded username, then when a request for the target domain comes in that decodes to the exact URL, it will serve the attacker's HTML instead of the real HTML. On Squid servers that also act as reverse proxies, this allows an attacker to gain access to features that only reverse proxies can use, such as ESI.

## References
- http://www.squid-cache.org/Versions/v4/
- http://www.squid-cache.org/Versions/v4/changesets/
- https://gitlab.com/jeriko.one/security/-/blob/master/squid/CVEs/CVE-2019-12520.txt
- https://lists.debian.org/debian-lts-announce/2020/07/msg00009.html
- https://security.netapp.com/advisory/ntap-20210205-0006/
- https://usn.ubuntu.com/4446-1/
- https://www.debian.org/security/2020/dsa-4682
- https://github.com/squid-cache/squid/commits/v4
