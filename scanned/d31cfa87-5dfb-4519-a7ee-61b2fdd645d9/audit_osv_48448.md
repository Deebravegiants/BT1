# [C] CVE-2017-7800

## Summary
Severity: Critical
Advisory: CVE-2017-7800
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-06-11
Source: https://osv.dev/vulnerability/CVE-2017-7800
Type: osv

## Details
A use-after-free vulnerability can occur in WebSockets when the object holding the connection is freed before the disconnection operation is finished. This results in an exploitable crash. This vulnerability affects Thunderbird < 52.3, Firefox ESR < 52.3, and Firefox < 55.

## References
- https://access.redhat.com/errata/RHSA-2017:2456
- https://www.debian.org/security/2017/dsa-3968
- https://www.mozilla.org/security/advisories/mfsa2017-18/
- https://www.mozilla.org/security/advisories/mfsa2017-20/
- http://www.securityfocus.com/bid/100196
- http://www.securitytracker.com/id/1039124
- https://access.redhat.com/errata/RHSA-2017:2534
- https://security.gentoo.org/glsa/201803-14
- https://www.debian.org/security/2017/dsa-3928
- https://www.mozilla.org/security/advisories/mfsa2017-19/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1374047
