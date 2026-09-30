# [H] CVE-2022-29909

## Summary
Severity: High
Advisory: CVE-2022-29909
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-12-22
Source: https://osv.dev/vulnerability/CVE-2022-29909
Type: osv

## Details
Documents in deeply-nested cross-origin browsing contexts could have obtained permissions granted to the top-level origin, bypassing the existing prompt and wrongfully inheriting the top-level permissions. This vulnerability affects Thunderbird < 91.9, Firefox ESR < 91.9, and Firefox < 100.

## References
- https://www.mozilla.org/security/advisories/mfsa2022-16/
- https://www.mozilla.org/security/advisories/mfsa2022-17/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1755081
- https://www.mozilla.org/security/advisories/mfsa2022-18/
