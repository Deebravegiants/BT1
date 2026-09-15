# [M] CVE-2021-23969

## Summary
Severity: Medium
Advisory: CVE-2021-23969
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:N)
Published: 2021-02-26
Source: https://osv.dev/vulnerability/CVE-2021-23969
Type: osv

## Details
As specified in the W3C Content Security Policy draft, when creating a violation report, "User agents need to ensure that the source file is the URL requested by the page, pre-redirects. If that’s not possible, user agents need to strip the URL down to an origin to avoid unintentional leakage." Under certain types of redirects, Firefox incorrectly set the source file to be the destination of the redirects. This was fixed to be the redirect destination's origin. This vulnerability affects Firefox < 86, Thunderbird < 78.8, and Firefox ESR < 78.8.

## References
- https://www.mozilla.org/security/advisories/mfsa2021-08/
- https://www.mozilla.org/security/advisories/mfsa2021-09/
- https://lists.debian.org/debian-lts-announce/2021/03/msg00000.html
- https://security.gentoo.org/glsa/202104-09
- https://security.gentoo.org/glsa/202104-10
- https://www.debian.org/security/2021/dsa-4866
- https://www.mozilla.org/security/advisories/mfsa2021-07/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1542194
