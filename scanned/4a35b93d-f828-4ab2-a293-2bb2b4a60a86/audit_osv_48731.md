# [H] CVE-2018-12361

## Summary
Severity: High
Advisory: CVE-2018-12361
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-10-18
Source: https://osv.dev/vulnerability/CVE-2018-12361
Type: osv

## Details
An integer overflow can occur in the SwizzleData code while calculating buffer sizes. The overflowed value is used for subsequent graphics computations when their inputs are not sanitized which results in a potentially exploitable crash. This vulnerability affects Thunderbird < 60, Firefox ESR < 60.1, and Firefox < 61.

## References
- http://www.securitytracker.com/id/1041193
- https://lists.debian.org/debian-lts-announce/2018/11/msg00011.html
- https://security.gentoo.org/glsa/201810-01
- https://usn.ubuntu.com/3705-1/
- https://www.mozilla.org/security/advisories/mfsa2018-15/
- https://www.mozilla.org/security/advisories/mfsa2018-19/
- http://www.securityfocus.com/bid/104558
- https://security.gentoo.org/glsa/201811-13
- https://www.debian.org/security/2018/dsa-4295
- https://www.mozilla.org/security/advisories/mfsa2018-16/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1463244
