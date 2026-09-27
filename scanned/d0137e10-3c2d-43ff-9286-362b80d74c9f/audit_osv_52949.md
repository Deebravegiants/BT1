# [M] CVE-2022-22760

## Summary
Severity: Medium
Advisory: CVE-2022-22760
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2022-12-22
Source: https://osv.dev/vulnerability/CVE-2022-22760
Type: osv

## Details
When importing resources using Web Workers, error messages would distinguish the difference between <code>application/javascript</code> responses and non-script responses. This could have been abused to learn information cross-origin. This vulnerability affects Firefox < 97, Thunderbird < 91.6, and Firefox ESR < 91.6.

## References
- https://www.mozilla.org/security/advisories/mfsa2022-06/
- https://www.mozilla.org/security/advisories/mfsa2022-04/
- https://www.mozilla.org/security/advisories/mfsa2022-05/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1740985
- https://bugzilla.mozilla.org/show_bug.cgi?id=1748503
