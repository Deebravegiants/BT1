# [M] CVE-2023-25742

## Summary
Severity: Medium
Advisory: CVE-2023-25742
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-06-02
Source: https://osv.dev/vulnerability/CVE-2023-25742
Type: osv

## Details
When importing a SPKI RSA public key as ECDSA P-256, the key would be handled incorrectly causing the tab to crash. This vulnerability affects Firefox < 110, Thunderbird < 102.8, and Firefox ESR < 102.8.

## References
- https://www.mozilla.org/security/advisories/mfsa2023-05/
- https://www.mozilla.org/security/advisories/mfsa2023-06/
- https://www.mozilla.org/security/advisories/mfsa2023-07/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1813424
