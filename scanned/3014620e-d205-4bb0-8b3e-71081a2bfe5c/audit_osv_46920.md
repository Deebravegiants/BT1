# [H] CVE-2015-8027

## Summary
Severity: High
Advisory: CVE-2015-8027
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-01-02
Source: https://osv.dev/vulnerability/CVE-2015-8027
Type: osv

## Details
Node.js 0.12.x before 0.12.9, 4.x before 4.2.3, and 5.x before 5.1.1 does not ensure the availability of a parser for each HTTP socket, which allows remote attackers to cause a denial of service (uncaughtException and service outage) via a pipelined HTTP request.

## References
- http://www-01.ibm.com/support/docview.wss?uid=swg1IV79524
- http://www-01.ibm.com/support/docview.wss?uid=swg21972419
- https://nodejs.org/en/blog/vulnerability/cve-2015-8027_cve-2015-6764/
- https://nodejs.org/en/blog/vulnerability/december-2015-security-releases/
- https://security.gentoo.org/glsa/201612-43
- http://lists.opensuse.org/opensuse-updates/2016-01/msg00045.html
- http://www.securityfocus.com/bid/78207
