# [H] CVE-2022-31740

## Summary
Severity: High
Advisory: CVE-2022-31740
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-12-22
Source: https://osv.dev/vulnerability/CVE-2022-31740
Type: osv

## Details
On arm64, WASM code could have resulted in incorrect assembly generation leading to a register allocation problem, and a potentially exploitable crash. This vulnerability affects Thunderbird < 91.10, Firefox < 101, and Firefox ESR < 91.10.

## References
- https://www.mozilla.org/security/advisories/mfsa2022-22/
- https://www.mozilla.org/security/advisories/mfsa2022-20/
- https://www.mozilla.org/security/advisories/mfsa2022-21/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1766806
