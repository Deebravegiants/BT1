# [M] CVE-2021-29945

## Summary
Severity: Medium
Advisory: CVE-2021-29945
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-06-24
Source: https://osv.dev/vulnerability/CVE-2021-29945
Type: osv

## Details
The WebAssembly JIT could miscalculate the size of a return type, which could lead to a null read and result in a crash. *Note: This issue only affected x86-32 platforms. Other platforms are unaffected.*. This vulnerability affects Firefox ESR < 78.10, Thunderbird < 78.10, and Firefox < 88.

## References
- https://www.mozilla.org/security/advisories/mfsa2021-14/
- https://www.mozilla.org/security/advisories/mfsa2021-15/
- https://www.mozilla.org/security/advisories/mfsa2021-16/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1700690
