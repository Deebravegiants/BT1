# [H] CVE-2024-7652

## Summary
Severity: High
Advisory: CVE-2024-7652
Aliases: GHSA-g38c-wh3c-5h9r
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-09-06
Source: https://osv.dev/vulnerability/CVE-2024-7652
Type: osv

## Details
An error in the ECMA-262 specification relating to Async Generators could have resulted in a type confusion, potentially leading to memory corruption and an exploitable crash. This vulnerability affects Firefox < 128, Firefox ESR < 115.13, Thunderbird < 115.13, and Thunderbird < 128.

## References
- https://github.com/tc39/ecma262/security/advisories/GHSA-g38c-wh3c-5h9r
- https://www.mozilla.org/security/advisories/mfsa2024-29/
- https://www.mozilla.org/security/advisories/mfsa2024-30/
- https://www.mozilla.org/security/advisories/mfsa2024-31/
- https://www.mozilla.org/security/advisories/mfsa2024-32/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1901411
