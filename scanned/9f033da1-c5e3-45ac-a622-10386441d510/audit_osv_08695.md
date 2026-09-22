# [M] CVE-2016-5325

## Summary
Severity: Medium
Advisory: CVE-2016-5325
CVSS: 6.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2016-10-10
Source: https://osv.dev/vulnerability/CVE-2016-5325
Type: osv

## Details
CRLF injection vulnerability in the ServerResponse#writeHead function in Node.js 0.10.x before 0.10.47, 0.12.x before 0.12.16, 4.x before 4.6.0, and 6.x before 6.7.0 allows remote attackers to inject arbitrary HTTP headers and conduct HTTP response splitting attacks via the reason argument.

## References
- http://www.securityfocus.com/bid/93483
- http://lists.opensuse.org/opensuse-security-announce/2016-10/msg00013.html
- http://rhn.redhat.com/errata/RHSA-2017-0002.html
- https://access.redhat.com/errata/RHSA-2016:2101
- https://security.gentoo.org/glsa/201612-43
- https://github.com/nodejs/node/commit/c0f13e56a20f9bde5a67d873a7f9564487160762
- https://nodejs.org/en/blog/vulnerability/september-2016-security-releases/
