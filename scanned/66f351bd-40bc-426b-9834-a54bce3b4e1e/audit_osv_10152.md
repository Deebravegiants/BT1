# [C] CVE-2017-14064

## Summary
Severity: Critical
Advisory: CVE-2017-14064
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-08-31
Source: https://osv.dev/vulnerability/CVE-2017-14064
Type: osv

## Details
Ruby through 2.2.7, 2.3.x through 2.3.4, and 2.4.x through 2.4.1 can expose arbitrary memory during a JSON.generate call. The issues lies in using strdup in ext/json/ext/generator/generator.c, which will stop after encountering a '\0' byte, returning a pointer to a string of length zero, which is not the length stored in space_len.

## References
- http://www.securityfocus.com/bid/100890
- http://www.securitytracker.com/id/1039363
- http://www.securitytracker.com/id/1042004
- https://access.redhat.com/errata/RHSA-2017:3485
- https://access.redhat.com/errata/RHSA-2018:0378
- https://access.redhat.com/errata/RHSA-2018:0583
- https://access.redhat.com/errata/RHSA-2018:0585
- https://lists.debian.org/debian-lts-announce/2018/07/msg00012.html
- https://security.gentoo.org/glsa/201710-18
- https://usn.ubuntu.com/3685-1/
- https://www.debian.org/security/2017/dsa-3966
- https://www.ruby-lang.org/en/news/2017/09/14/ruby-2-2-8-released/
- https://www.ruby-lang.org/en/news/2017/09/14/ruby-2-3-5-released/
- https://bugs.ruby-lang.org/issues/13853
- https://github.com/flori/json/commit/8f782fd8e181d9cfe9387ded43a5ca9692266b85
- https://hackerone.com/reports/209949
