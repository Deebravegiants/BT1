# [M] CVE-2021-43538

## Summary
Severity: Medium
Advisory: CVE-2021-43538
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N)
Published: 2021-12-08
Source: https://osv.dev/vulnerability/CVE-2021-43538
Type: osv

## Details
By misusing a race in our notification code, an attacker could have forcefully hidden the notification for pages that had received full screen and pointer lock access, which could have been used for spoofing attacks. This vulnerability affects Thunderbird < 91.4.0, Firefox ESR < 91.4.0, and Firefox < 95.

## References
- https://lists.debian.org/debian-lts-announce/2022/01/msg00001.html
- https://security.gentoo.org/glsa/202208-14
- https://www.debian.org/security/2022/dsa-5034
- https://www.mozilla.org/security/advisories/mfsa2021-52/
- https://www.mozilla.org/security/advisories/mfsa2021-54/
- https://lists.debian.org/debian-lts-announce/2021/12/msg00030.html
- https://security.gentoo.org/glsa/202202-03
- https://www.debian.org/security/2021/dsa-5026
- https://www.mozilla.org/security/advisories/mfsa2021-53/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1739091
