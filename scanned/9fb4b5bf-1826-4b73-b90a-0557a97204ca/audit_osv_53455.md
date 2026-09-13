# [H] CVE-2022-42927

## Summary
Severity: High
Advisory: CVE-2022-42927
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N)
Published: 2022-12-22
Source: https://osv.dev/vulnerability/CVE-2022-42927
Type: osv

## Details
A same-origin policy violation could have allowed the theft of cross-origin URL entries, leaking the result of a redirect, via `performance.getEntries()`. This vulnerability affects Firefox < 106, Firefox ESR < 102.4, and Thunderbird < 102.4.

## References
- https://www.mozilla.org/security/advisories/mfsa2022-44/
- https://www.mozilla.org/security/advisories/mfsa2022-45/
- https://www.mozilla.org/security/advisories/mfsa2022-46/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1789128
