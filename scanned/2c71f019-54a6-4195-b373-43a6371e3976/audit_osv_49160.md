# [C] CVE-2018-5099

## Summary
Severity: Critical
Advisory: CVE-2018-5099
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-06-11
Source: https://osv.dev/vulnerability/CVE-2018-5099
Type: osv

## Details
A use-after-free vulnerability can occur when the widget listener is holding strong references to browser objects that have previously been freed, resulting in a potentially exploitable crash when these references are used. This vulnerability affects Thunderbird < 52.6, Firefox ESR < 52.6, and Firefox < 58.

## References
- https://access.redhat.com/errata/RHSA-2018:0122
- https://access.redhat.com/errata/RHSA-2018:0262
- https://lists.debian.org/debian-lts-announce/2018/01/msg00030.html
- https://lists.debian.org/debian-lts-announce/2018/01/msg00036.html
- https://www.debian.org/security/2018/dsa-4096
- https://www.mozilla.org/security/advisories/mfsa2018-02/
- https://www.mozilla.org/security/advisories/mfsa2018-04/
- http://www.securityfocus.com/bid/102783
- http://www.securitytracker.com/id/1040270
- https://usn.ubuntu.com/3544-1/
- https://www.debian.org/security/2018/dsa-4102
- https://www.mozilla.org/security/advisories/mfsa2018-03/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1416878
