# [M] CVE-2018-12367

## Summary
Severity: Medium
Advisory: CVE-2018-12367
CVSS: 4.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:N)
Published: 2018-10-18
Source: https://osv.dev/vulnerability/CVE-2018-12367
Type: osv

## Details
In the previous mitigations for Spectre, the resolution or precision of various methods was reduced to counteract the ability to measure precise time intervals. In that work PerformanceNavigationTiming was not adjusted but it was found that it could be used as a precision timer. This vulnerability affects Thunderbird < 60, Firefox ESR < 60.1, and Firefox < 61.

## References
- https://security.gentoo.org/glsa/201810-01
- https://www.debian.org/security/2018/dsa-4295
- https://www.mozilla.org/security/advisories/mfsa2018-15/
- https://www.mozilla.org/security/advisories/mfsa2018-16/
- https://www.mozilla.org/security/advisories/mfsa2018-19/
- http://www.securityfocus.com/bid/104561
- http://www.securitytracker.com/id/1041193
- https://lists.debian.org/debian-lts-announce/2018/11/msg00011.html
- https://security.gentoo.org/glsa/201811-13
- https://usn.ubuntu.com/3705-1/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1462891
