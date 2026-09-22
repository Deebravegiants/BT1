# [H] CVE-2020-26974

## Summary
Severity: High
Advisory: CVE-2020-26974
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-01-07
Source: https://osv.dev/vulnerability/CVE-2020-26974
Type: osv

## Details
When flex-basis was used on a table wrapper, a StyleGenericFlexBasis object could have been incorrectly cast to the wrong type. This resulted in a heap user-after-free, memory corruption, and a potentially exploitable crash. This vulnerability affects Firefox < 84, Thunderbird < 78.6, and Firefox ESR < 78.6.

## References
- https://www.mozilla.org/security/advisories/mfsa2020-54/
- https://www.mozilla.org/security/advisories/mfsa2020-55/
- https://www.mozilla.org/security/advisories/mfsa2020-56/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1681022
