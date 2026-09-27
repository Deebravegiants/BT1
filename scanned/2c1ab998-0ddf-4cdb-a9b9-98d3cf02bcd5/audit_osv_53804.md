# [M] CVE-2023-25751

## Summary
Severity: Medium
Advisory: CVE-2023-25751
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-06-02
Source: https://osv.dev/vulnerability/CVE-2023-25751
Type: osv

## Details
Sometimes, when invalidating JIT code while following an iterator, the newly generated code could be overwritten incorrectly. This could lead to a potentially exploitable crash. This vulnerability affects Firefox < 111, Firefox ESR < 102.9, and Thunderbird < 102.9.

## References
- https://www.mozilla.org/security/advisories/mfsa2023-10/
- https://www.mozilla.org/security/advisories/mfsa2023-11/
- https://www.mozilla.org/security/advisories/mfsa2023-09/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1814899
