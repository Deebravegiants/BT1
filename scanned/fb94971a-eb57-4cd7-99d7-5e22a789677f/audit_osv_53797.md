# [H] CVE-2023-25732

## Summary
Severity: High
Advisory: CVE-2023-25732
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-06-02
Source: https://osv.dev/vulnerability/CVE-2023-25732
Type: osv

## Details
When encoding data from an <code>inputStream</code> in <code>xpcom</code> the size of the input being encoded was not correctly calculated potentially leading to an out of bounds memory write. This vulnerability affects Firefox < 110, Thunderbird < 102.8, and Firefox ESR < 102.8.

## References
- https://www.mozilla.org/security/advisories/mfsa2023-05/
- https://www.mozilla.org/security/advisories/mfsa2023-06/
- https://www.mozilla.org/security/advisories/mfsa2023-07/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1804564
