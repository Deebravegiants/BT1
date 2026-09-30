# [M] CVE-2018-5117

## Summary
Severity: Medium
Advisory: CVE-2018-5117
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2018-06-11
Source: https://osv.dev/vulnerability/CVE-2018-5117
Type: osv

## Details
If right-to-left text is used in the addressbar with left-to-right alignment, it is possible in some circumstances to scroll this text to spoof the displayed URL. This issue could result in the wrong URL being displayed as a location, which can mislead users to believe they are on a different site than the one loaded. This vulnerability affects Thunderbird < 52.6, Firefox ESR < 52.6, and Firefox < 58.

## References
- https://www.mozilla.org/security/advisories/mfsa2018-02/
- http://www.securityfocus.com/bid/102783
- http://www.securitytracker.com/id/1040270
- https://lists.debian.org/debian-lts-announce/2018/01/msg00030.html
- https://lists.debian.org/debian-lts-announce/2018/01/msg00036.html
- https://usn.ubuntu.com/3544-1/
- https://www.debian.org/security/2018/dsa-4096
- https://www.mozilla.org/security/advisories/mfsa2018-03/
- https://www.mozilla.org/security/advisories/mfsa2018-04/
- https://access.redhat.com/errata/RHSA-2018:0122
- https://access.redhat.com/errata/RHSA-2018:0262
- https://www.debian.org/security/2018/dsa-4102
- https://bugzilla.mozilla.org/show_bug.cgi?id=1395508
