# [C] CVE-2017-6969

## Summary
Severity: Critical
Advisory: CVE-2017-6969
CVSS: 9.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2017-03-17
Source: https://osv.dev/vulnerability/CVE-2017-6969
Type: osv

## Details
readelf in GNU Binutils 2.28 is vulnerable to a heap-based buffer over-read while processing corrupt RL78 binaries. The vulnerability can trigger program crashes. It may lead to an information leak as well.

## References
- http://www.securityfocus.com/bid/97065
- https://security.gentoo.org/glsa/201709-02
- https://sourceware.org/bugzilla/show_bug.cgi?id=21156
