# [H] CVE-2018-7164

## Summary
Severity: High
Advisory: CVE-2018-7164
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-06-13
Source: https://osv.dev/vulnerability/CVE-2018-7164
Type: osv

## Details
Node.js versions 9.7.0 and later and 10.x are vulnerable and the severity is MEDIUM. A bug introduced in 9.7.0 increases the memory consumed when reading from the network into JavaScript using the net.Socket object directly as a stream. An attacker could use this cause a denial of service by sending tiny chunks of data in short succession. This vulnerability was restored by reverting to the prior behaviour.

## References
- http://www.securityfocus.com/bid/104463
- https://nodejs.org/en/blog/vulnerability/june-2018-security-releases/
- https://security.gentoo.org/glsa/202003-48
