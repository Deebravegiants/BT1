# [H] CVE-2021-38496

## Summary
Severity: High
Advisory: CVE-2021-38496
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-11-03
Source: https://osv.dev/vulnerability/CVE-2021-38496
Type: osv

## Details
During operations on MessageTasks, a task may have been removed while it was still scheduled, resulting in memory corruption and a potentially exploitable crash. This vulnerability affects Thunderbird < 78.15, Thunderbird < 91.2, Firefox ESR < 91.2, Firefox ESR < 78.15, and Firefox < 93.

## References
- https://lists.debian.org/debian-lts-announce/2022/01/msg00001.html
- https://www.mozilla.org/security/advisories/mfsa2021-43/
- https://www.mozilla.org/security/advisories/mfsa2021-44/
- https://www.mozilla.org/security/advisories/mfsa2021-45/
- https://www.mozilla.org/security/advisories/mfsa2021-46/
- https://www.mozilla.org/security/advisories/mfsa2021-47/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1725335
- https://www.debian.org/security/2022/dsa-5034
