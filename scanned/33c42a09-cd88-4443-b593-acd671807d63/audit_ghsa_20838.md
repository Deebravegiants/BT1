# [M] YetiForce CRM vulnerable to stored Cross-site Scripting via WidgetsManagement module

## Summary
Severity: Medium
Advisory: GHSA-2qf8-h7pr-x2r8
CVE: CVE-2022-2924
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-09-21
Source: https://github.com/advisories/GHSA-2qf8-h7pr-x2r8
Type: github-advisory

## Affected
- Packagist: `yetiforce/yetiforce-crm` — affected >=0

## Details
YetiForce CRM versions 6.4.0 and prior are vulnerable to cross-site scripting via the `WidgetsManagement` module. A patch is available at commit b716ecea340783b842498425faa029800bd30420.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-2924
- https://github.com/yetiforcecompany/yetiforcecrm/commit/b716ecea340783b842498425faa029800bd30420
- https://github.com/YetiForceCompany/YetiForceCRM
- https://huntr.dev/bounties/f0f3aded-6e97-4cf2-980a-c90f2c6ca0e0
