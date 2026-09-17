# [C] CVE-2017-5464

## Summary
Severity: Critical
Advisory: CVE-2017-5464
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-06-11
Source: https://osv.dev/vulnerability/CVE-2017-5464
Type: osv

## Details
During DOM manipulations of the accessibility tree through script, the DOM tree can become out of sync with the accessibility tree, leading to memory corruption and a potentially exploitable crash. This vulnerability affects Thunderbird < 52.1, Firefox ESR < 45.9, Firefox ESR < 52.1, and Firefox < 53.

## References
- http://www.securitytracker.com/id/1038320
- https://www.debian.org/security/2017/dsa-3831
- https://www.mozilla.org/security/advisories/mfsa2017-11/
- https://www.mozilla.org/security/advisories/mfsa2017-12/
- http://www.securityfocus.com/bid/97940
- https://access.redhat.com/errata/RHSA-2017:1104
- https://access.redhat.com/errata/RHSA-2017:1106
- https://access.redhat.com/errata/RHSA-2017:1201
- https://www.mozilla.org/security/advisories/mfsa2017-10/
- https://www.mozilla.org/security/advisories/mfsa2017-13/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1347075
