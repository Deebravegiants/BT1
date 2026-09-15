# [C] CVE-2017-5438

## Summary
Severity: Critical
Advisory: CVE-2017-5438
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-06-11
Source: https://osv.dev/vulnerability/CVE-2017-5438
Type: osv

## Details
A use-after-free vulnerability during XSLT processing due to the result handler being held by a freed handler during handling. This results in a potentially exploitable crash. This vulnerability affects Thunderbird < 52.1, Firefox ESR < 45.9, Firefox ESR < 52.1, and Firefox < 53.

## References
- https://www.mozilla.org/security/advisories/mfsa2017-13/
- http://www.securityfocus.com/bid/97940
- http://www.securitytracker.com/id/1038320
- https://access.redhat.com/errata/RHSA-2017:1106
- https://www.mozilla.org/security/advisories/mfsa2017-10/
- https://www.mozilla.org/security/advisories/mfsa2017-11/
- https://www.mozilla.org/security/advisories/mfsa2017-12/
- https://access.redhat.com/errata/RHSA-2017:1104
- https://access.redhat.com/errata/RHSA-2017:1201
- https://www.debian.org/security/2017/dsa-3831
- https://bugzilla.mozilla.org/show_bug.cgi?id=1336828
