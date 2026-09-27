# [M] CVE-2022-40957

## Summary
Severity: Medium
Advisory: CVE-2022-40957
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-12-22
Source: https://osv.dev/vulnerability/CVE-2022-40957
Type: osv

## Details
Inconsistent data in instruction and data cache when creating wasm code could lead to a potentially exploitable crash.<br>*This bug only affects Firefox on ARM64 platforms.*. This vulnerability affects Firefox ESR < 102.3, Thunderbird < 102.3, and Firefox < 105.

## References
- https://www.mozilla.org/security/advisories/mfsa2022-40/
- https://www.mozilla.org/security/advisories/mfsa2022-41/
- https://www.mozilla.org/security/advisories/mfsa2022-42/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1777604
