# [M] CVE-2021-38508

## Summary
Severity: Medium
Advisory: CVE-2021-38508
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N)
Published: 2021-12-08
Source: https://osv.dev/vulnerability/CVE-2021-38508
Type: osv

## Details
By displaying a form validity message in the correct location at the same time as a permission prompt (such as for geolocation), the validity message could have obscured the prompt, resulting in the user potentially being tricked into granting the permission. This vulnerability affects Firefox < 94, Thunderbird < 91.3, and Firefox ESR < 91.3.

## References
- https://lists.debian.org/debian-lts-announce/2021/12/msg00030.html
- https://lists.debian.org/debian-lts-announce/2022/01/msg00001.html
- https://www.debian.org/security/2022/dsa-5034
- https://www.mozilla.org/security/advisories/mfsa2021-48/
- https://www.mozilla.org/security/advisories/mfsa2021-49/
- https://www.mozilla.org/security/advisories/mfsa2021-50/
- https://security.gentoo.org/glsa/202202-03
- https://security.gentoo.org/glsa/202208-14
- https://www.debian.org/security/2021/dsa-5026
- https://bugzilla.mozilla.org/show_bug.cgi?id=1366818
