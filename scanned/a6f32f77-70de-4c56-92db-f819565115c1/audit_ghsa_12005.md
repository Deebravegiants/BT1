# [H] Azure Blob Storage for Craft CMS Potential Sensitive Information Disclosure vulnerability

## Summary
Severity: High
Advisory: GHSA-q6fm-p73f-x862
CVE: CVE-2026-32268
CWE: CWE-862
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-16
Source: https://github.com/advisories/GHSA-q6fm-p73f-x862
Type: github-advisory

## Affected
- Packagist: `craftcms/azure-blob` — affected >=2.0.0-beta.1 <2.1.1

## Details
Unauthenticated users can view a list of buckets the plugin has access to.

The `DefaultController->actionLoadContainerData()` endpoint allows unauthenticated users with a valid CSRF token to view a list of buckets that the plugin is allowed to see.

Because Azure can return sensitive data in error messages, additional attack vectors are also exposed.

Users should update to version 2.1.1 of the plugin to mitigate the issue.

## References
- https://github.com/craftcms/azure-blob/security/advisories/GHSA-q6fm-p73f-x862
- https://nvd.nist.gov/vuln/detail/CVE-2026-32268
- https://github.com/craftcms/azure-blob/commit/cf69db45f393b3508a32f89ac8235554a2f026ff
- https://github.com/craftcms/azure-blob
