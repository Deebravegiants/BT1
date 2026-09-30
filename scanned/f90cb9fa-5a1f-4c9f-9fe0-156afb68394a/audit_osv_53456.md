# [H] CVE-2022-42928

## Summary
Severity: High
Advisory: CVE-2022-42928
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-12-22
Source: https://osv.dev/vulnerability/CVE-2022-42928
Type: osv

## Details
Certain types of allocations were missing annotations that, if the Garbage Collector was in a specific state, could have lead to memory corruption and a potentially exploitable crash. This vulnerability affects Firefox < 106, Firefox ESR < 102.4, and Thunderbird < 102.4.

## References
- https://www.mozilla.org/security/advisories/mfsa2022-44/
- https://www.mozilla.org/security/advisories/mfsa2022-45/
- https://www.mozilla.org/security/advisories/mfsa2022-46/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1791520
