# [H] CVE-2018-7161

## Summary
Severity: High
Advisory: CVE-2018-7161
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-06-13
Source: https://osv.dev/vulnerability/CVE-2018-7161
Type: osv

## Details
All versions of Node.js 8.x, 9.x, and 10.x are vulnerable and the severity is HIGH. An attacker can cause a denial of service (DoS) by causing a node server providing an http2 server to crash. This can be accomplished by interacting with the http2 server in a manner that triggers a cleanup bug where objects are used in native code after they are no longer available. This has been addressed by updating the http2 implementation.

## References
- http://www.securityfocus.com/bid/106363
- https://security.gentoo.org/glsa/202003-48
- https://nodejs.org/en/blog/vulnerability/june-2018-security-releases/
