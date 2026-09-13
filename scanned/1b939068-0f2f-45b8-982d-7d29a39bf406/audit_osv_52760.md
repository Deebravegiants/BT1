# [M] CVE-2022-1097

## Summary
Severity: Medium
Advisory: CVE-2022-1097
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-12-22
Source: https://osv.dev/vulnerability/CVE-2022-1097
Type: osv

## Details
<code>NSSToken</code> objects were referenced via direct points, and could have been accessed in an unsafe way on different threads, leading to a use-after-free and potentially exploitable crash. This vulnerability affects Thunderbird < 91.8, Firefox < 99, and Firefox ESR < 91.8.

## References
- https://www.mozilla.org/security/advisories/mfsa2022-13/
- https://www.mozilla.org/security/advisories/mfsa2022-14/
- https://www.mozilla.org/security/advisories/mfsa2022-15/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1745667
