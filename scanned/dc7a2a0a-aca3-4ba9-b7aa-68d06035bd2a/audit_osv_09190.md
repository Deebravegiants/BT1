# [H] CVE-2016-8860

## Summary
Severity: High
Advisory: CVE-2016-8860
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-01-04
Source: https://osv.dev/vulnerability/CVE-2016-8860
Type: osv

## Details
Tor before 0.2.8.9 and 0.2.9.x before 0.2.9.4-alpha had internal functions that were entitled to expect that buf_t data had NUL termination, but the implementation of or/buffers.c did not ensure that NUL termination was present, which allows remote attackers to cause a denial of service (client, hidden service, relay, or authority crash) via crafted data.

## References
- http://www.securityfocus.com/bid/95116
- http://openwall.com/lists/oss-security/2016/10/19/11
- http://www.debian.org/security/2016/dsa-3694
- https://blog.torproject.org/blog/tor-0289-released-important-fixes
- https://security.gentoo.org/glsa/201612-45
- https://trac.torproject.org/projects/tor/ticket/20384
- https://github.com/torproject/tor/commit/3cea86eb2fbb65949673eb4ba8ebb695c87a57ce
