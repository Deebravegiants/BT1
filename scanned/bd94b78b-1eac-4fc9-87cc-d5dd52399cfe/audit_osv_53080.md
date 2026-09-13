# [M] CVE-2022-28285

## Summary
Severity: Medium
Advisory: CVE-2022-28285
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2022-12-22
Source: https://osv.dev/vulnerability/CVE-2022-28285
Type: osv

## Details
When generating the assembly code for <code>MLoadTypedArrayElementHole</code>, an incorrect AliasSet was used. In conjunction with another vulnerability this could have been used for an out of bounds memory read. This vulnerability affects Thunderbird < 91.8, Firefox < 99, and Firefox ESR < 91.8.

## References
- https://bugzilla.mozilla.org/show_bug.cgi?id=1756957
- https://www.mozilla.org/security/advisories/mfsa2022-13/
- https://www.mozilla.org/security/advisories/mfsa2022-14/
- https://www.mozilla.org/security/advisories/mfsa2022-15/
