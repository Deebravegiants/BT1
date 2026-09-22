# [H] CVE-2021-23960

## Summary
Severity: High
Advisory: CVE-2021-23960
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-02-26
Source: https://osv.dev/vulnerability/CVE-2021-23960
Type: osv

## Details
Performing garbage collection on re-declared JavaScript variables resulted in a user-after-poison, and a potentially exploitable crash. This vulnerability affects Firefox < 85, Thunderbird < 78.7, and Firefox ESR < 78.7.

## References
- https://www.mozilla.org/security/advisories/mfsa2021-04/
- https://www.mozilla.org/security/advisories/mfsa2021-05/
- https://www.mozilla.org/security/advisories/mfsa2021-03/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1675755
