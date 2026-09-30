# [M] Pimcore Admin Classic Bundle allows user enumeration

## Summary
Severity: Medium
Advisory: GHSA-vr5f-php7-rg24
CVE: CVE-2025-24980
CWE: CWE-204
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-02-07
Source: https://github.com/advisories/GHSA-vr5f-php7-rg24
Type: github-advisory

## Affected
- Packagist: `pimcore/admin-ui-classic-bundle` — affected >=0 <1.7.4

## Details
pimcore/admin-ui-classic-bundle provides a Backend UI for Pimcore. In affected versions an error message discloses existing accounts and leads to user enumeration on the target via "Forgot password" function. No generic error message has been implemented. This issue has been addressed in version 1.7.4 and all users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/pimcore/admin-ui-classic-bundle/security/advisories/GHSA-vr5f-php7-rg24
- https://nvd.nist.gov/vuln/detail/CVE-2025-24980
- https://github.com/pimcore/admin-ui-classic-bundle/pull/808
- https://github.com/pimcore/admin-ui-classic-bundle/commit/96ae555578c3b4df368092d71e07a6c4ddf8fbe9
- https://github.com/pimcore/admin-ui-classic-bundle
