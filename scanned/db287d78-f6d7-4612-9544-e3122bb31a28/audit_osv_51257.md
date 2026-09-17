# [H] CVE-2021-23954

## Summary
Severity: High
Advisory: CVE-2021-23954
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-02-26
Source: https://osv.dev/vulnerability/CVE-2021-23954
Type: osv

## Details
Using the new logical assignment operators in a JavaScript switch statement could have caused a type confusion, leading to a memory corruption and a potentially exploitable crash. This vulnerability affects Firefox < 85, Thunderbird < 78.7, and Firefox ESR < 78.7.

## References
- https://www.mozilla.org/security/advisories/mfsa2021-03/
- https://www.mozilla.org/security/advisories/mfsa2021-04/
- https://www.mozilla.org/security/advisories/mfsa2021-05/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1684020
