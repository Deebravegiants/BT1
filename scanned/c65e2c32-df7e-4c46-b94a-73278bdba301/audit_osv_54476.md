# [H] CVE-2023-6864

## Summary
Severity: High
Advisory: CVE-2023-6864
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-12-19
Source: https://osv.dev/vulnerability/CVE-2023-6864
Type: osv

## Details
Memory safety bugs present in Firefox 120, Firefox ESR 115.5, and Thunderbird 115.5. Some of these bugs showed evidence of memory corruption and we presume that with enough effort some of these could have been exploited to run arbitrary code. This vulnerability affects Firefox ESR < 115.6, Thunderbird < 115.6, and Firefox < 121.

## References
- https://lists.debian.org/debian-lts-announce/2023/12/msg00020.html
- https://lists.debian.org/debian-lts-announce/2023/12/msg00021.html
- https://security.gentoo.org/glsa/202401-10
- https://www.mozilla.org/security/advisories/mfsa2023-54/
- https://www.mozilla.org/security/advisories/mfsa2023-55/
- https://www.mozilla.org/security/advisories/mfsa2023-56/
- https://www.debian.org/security/2023/dsa-5581
- https://www.debian.org/security/2023/dsa-5582
- https://bugzilla.mozilla.org/buglist.cgi?bug_id=1736385%2C1810805%2C1846328%2C1856090%2C1858033%2C1858509%2C1862089%2C1862777%2C1864015
