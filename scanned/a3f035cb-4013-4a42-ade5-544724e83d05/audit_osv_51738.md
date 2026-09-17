# [H] CVE-2021-38504

## Summary
Severity: High
Advisory: CVE-2021-38504
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-12-08
Source: https://osv.dev/vulnerability/CVE-2021-38504
Type: osv

## Details
When interacting with an HTML input element's file picker dialog with webkitdirectory set, a use-after-free could have resulted, leading to memory corruption and a potentially exploitable crash. This vulnerability affects Firefox < 94, Thunderbird < 91.3, and Firefox ESR < 91.3.

## References
- https://lists.debian.org/debian-lts-announce/2022/01/msg00001.html
- https://security.gentoo.org/glsa/202202-03
- https://www.mozilla.org/security/advisories/mfsa2021-49/
- https://www.mozilla.org/security/advisories/mfsa2021-50/
- https://lists.debian.org/debian-lts-announce/2021/12/msg00030.html
- https://security.gentoo.org/glsa/202208-14
- https://www.debian.org/security/2021/dsa-5026
- https://www.debian.org/security/2022/dsa-5034
- https://www.mozilla.org/security/advisories/mfsa2021-48/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1730156
