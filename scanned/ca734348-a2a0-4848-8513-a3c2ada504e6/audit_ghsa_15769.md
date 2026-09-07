# [M] Silverstripe Reports are still accessible even when `canView()` returns false

## Summary
Severity: Medium
Advisory: GHSA-89q6-98xx-4ffw
CVE: CVE-2024-29885
CWE: CWE-200, CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-07-17
Source: https://github.com/advisories/GHSA-89q6-98xx-4ffw
Type: github-advisory

## Affected
- Packagist: `silverstripe/reports` — affected >=0 <5.2.3

## Details
Reports can be accessed by their direct URL by any user who has access to view the reports admin section, even if the `canView()` method for that report returns `false`.

## References
- https://www.silverstripe.org/download/security-releases/cve-2024-29885

## References
- https://github.com/silverstripe/silverstripe-reports/security/advisories/GHSA-89q6-98xx-4ffw
- https://nvd.nist.gov/vuln/detail/CVE-2024-29885
- https://github.com/silverstripe/silverstripe-reports/commit/0351106c18ad4246d983b5f4e082c09c382121f4
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/reports/CVE-2024-29885.yaml
- https://github.com/silverstripe/silverstripe-reports
- https://www.silverstripe.org/download/security-releases/cve-2024-29885
