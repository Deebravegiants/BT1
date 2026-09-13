# [C] CVE-2021-38503

## Summary
Severity: Critical
Advisory: CVE-2021-38503
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2021-12-08
Source: https://osv.dev/vulnerability/CVE-2021-38503
Type: osv

## Details
The iframe sandbox rules were not correctly applied to XSLT stylesheets, allowing an iframe to bypass restrictions such as executing scripts or navigating the top-level frame. This vulnerability affects Firefox < 94, Thunderbird < 91.3, and Firefox ESR < 91.3.

## References
- https://lists.debian.org/debian-lts-announce/2021/12/msg00030.html
- https://security.gentoo.org/glsa/202202-03
- https://security.gentoo.org/glsa/202208-14
- https://www.debian.org/security/2021/dsa-5026
- https://www.mozilla.org/security/advisories/mfsa2021-48/
- https://www.mozilla.org/security/advisories/mfsa2021-49/
- https://www.mozilla.org/security/advisories/mfsa2021-50/
- https://lists.debian.org/debian-lts-announce/2022/01/msg00001.html
- https://www.debian.org/security/2022/dsa-5034
- https://bugzilla.mozilla.org/show_bug.cgi?id=1729517
