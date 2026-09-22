# [H] CVE-2018-7162

## Summary
Severity: High
Advisory: CVE-2018-7162
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-06-13
Source: https://osv.dev/vulnerability/CVE-2018-7162
Type: osv

## Details
All versions of Node.js 9.x and 10.x are vulnerable and the severity is HIGH. An attacker can cause a denial of service (DoS) by causing a node process which provides an http server supporting TLS server to crash. This can be accomplished by sending duplicate/unexpected messages during the handshake. This vulnerability has been addressed by updating the TLS implementation.

## References
- http://www.securityfocus.com/bid/104468
- https://nodejs.org/en/blog/vulnerability/june-2018-security-releases/
- https://security.gentoo.org/glsa/202003-48
