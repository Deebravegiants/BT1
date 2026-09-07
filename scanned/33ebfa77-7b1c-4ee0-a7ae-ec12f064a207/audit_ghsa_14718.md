# [M] Ibexa Admin UI vulnerable to Cross-site Scripting in a field that is used in the Content name pattern

## Summary
Severity: Medium
Advisory: GHSA-8w3p-gf85-qcch
CVE: CVE-2024-53864
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:L/VI:L/VA:L/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X (CVSS_V4)
Published: 2024-12-02
Source: https://github.com/advisories/GHSA-8w3p-gf85-qcch
Type: github-advisory

## Affected
- Packagist: `ibexa/admin-ui` — affected >=4.6.0 <4.6.14

## Details
### Impact
The Content name pattern is used to build Content names from one or more fields. An XSS vulnerability has been found in this mechanism. Content edit permission is required to exploit it. After the fix, any existing injected XSS will not run.

### Patches
- See "Patched versions.
- https://github.com/ibexa/admin-ui/commit/8ec824a8cf06c566ed88e4c21cc66f7ed42649fc

### Workarounds
None.

### References
- Advisory: https://developers.ibexa.co/security-advisories/ibexa-sa-2024-006-vulnerabilities-in-content-name-pattern-commerce-shop-and-varnish-vhost-templates
- Release notes: https://doc.ibexa.co/en/latest/update_and_migration/from_4.6/update_from_4.6/#v4614

## References
- https://github.com/ibexa/admin-ui/security/advisories/GHSA-8w3p-gf85-qcch
- https://nvd.nist.gov/vuln/detail/CVE-2024-53864
- https://github.com/ibexa/admin-ui/commit/8ec824a8cf06c566ed88e4c21cc66f7ed42649fc
- https://developers.ibexa.co/security-advisories/ibexa-sa-2024-006-vulnerabilities-in-content-name-pattern-commerce-shop-and-varnish-vhost-templates
- https://doc.ibexa.co/en/latest/update_and_migration/from_4.6/update_from_4.6/#v4614
- https://github.com/ibexa/admin-ui
