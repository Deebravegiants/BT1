# [M] CVE-2017-7830

## Summary
Severity: Medium
Advisory: CVE-2017-7830
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2018-06-11
Source: https://osv.dev/vulnerability/CVE-2017-7830
Type: osv

## Details
The Resource Timing API incorrectly revealed navigations in cross-origin iframes. This is a same-origin policy violation and could allow for data theft of URLs loaded by users. This vulnerability affects Firefox < 57, Firefox ESR < 52.5, and Thunderbird < 52.5.

## References
- https://www.debian.org/security/2017/dsa-4075
- https://www.mozilla.org/security/advisories/mfsa2017-24/
- https://www.mozilla.org/security/advisories/mfsa2017-25/
- https://www.mozilla.org/security/advisories/mfsa2017-26/
- https://access.redhat.com/errata/RHSA-2017:3247
- https://access.redhat.com/errata/RHSA-2017:3372
- https://lists.debian.org/debian-lts-announce/2017/11/msg00018.html
- https://www.debian.org/security/2017/dsa-4035
- https://www.debian.org/security/2017/dsa-4061
- http://www.securityfocus.com/bid/101832
- http://www.securitytracker.com/id/1039803
- https://lists.debian.org/debian-lts-announce/2017/12/msg00001.html
- https://bugzilla.mozilla.org/show_bug.cgi?id=1408990
