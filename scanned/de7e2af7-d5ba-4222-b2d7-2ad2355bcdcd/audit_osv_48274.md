# [C] CVE-2017-5472

## Summary
Severity: Critical
Advisory: CVE-2017-5472
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-06-11
Source: https://osv.dev/vulnerability/CVE-2017-5472
Type: osv

## Details
A use-after-free vulnerability with the frameloader during tree reconstruction while regenerating CSS layout when attempting to use a node in the tree that no longer exists. This results in a potentially exploitable crash. This vulnerability affects Firefox < 54, Firefox ESR < 52.2, and Thunderbird < 52.2.

## References
- https://www.mozilla.org/security/advisories/mfsa2017-15/
- https://www.mozilla.org/security/advisories/mfsa2017-17/
- https://access.redhat.com/errata/RHSA-2017:1440
- https://access.redhat.com/errata/RHSA-2017:1561
- https://www.debian.org/security/2017/dsa-3918
- https://www.mozilla.org/security/advisories/mfsa2017-16/
- http://www.securityfocus.com/bid/99040
- http://www.securitytracker.com/id/1038689
- https://www.debian.org/security/2017/dsa-3881
- https://bugzilla.mozilla.org/show_bug.cgi?id=1365602
