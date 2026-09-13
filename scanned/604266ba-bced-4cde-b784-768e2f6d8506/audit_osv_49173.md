# [C] CVE-2018-5147

## Summary
Severity: Critical
Advisory: CVE-2018-5147
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-06-11
Source: https://osv.dev/vulnerability/CVE-2018-5147
Type: osv

## Details
The libtremor library has the same flaw as CVE-2018-5146. This library is used by Firefox in place of libvorbis on Android and ARM platforms. This vulnerability affects Firefox ESR < 52.7.2 and Firefox < 59.0.1.

## References
- https://www.mozilla.org/security/advisories/mfsa2018-08/
- http://www.securityfocus.com/bid/103432
- http://www.securitytracker.com/id/1040544
- https://lists.debian.org/debian-lts-announce/2018/03/msg00016.html
- https://lists.debian.org/debian-lts-announce/2018/03/msg00022.html
- https://www.debian.org/security/2018/dsa-4141
- https://www.debian.org/security/2018/dsa-4143
- https://bugzilla.mozilla.org/show_bug.cgi?id=1446365
