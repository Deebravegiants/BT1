# [M] Umbraco CMS vulnerable to Generation of Error Message Containing Sensitive Information

## Summary
Severity: Medium
Advisory: GHSA-77gj-crhp-3gvx
CVE: CVE-2024-43376
CWE: CWE-209
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-08-20
Source: https://github.com/advisories/GHSA-77gj-crhp-3gvx
Type: github-advisory

## Affected
- NuGet: `Umbraco.Cms.Api.Management` — affected >=14.0.0 <14.1.2

## Details
### Impact
Some endpoints in the Management API can return stack trace information, even when Umbraco is not in debug mode.

### Explanation of the vulnerability
Management API endpoints leaked stack traces in case of Internal server errors, no matter if the debug setting was disabled.

E.g. when paging with negative numbers in some apis

## References
- https://github.com/umbraco/Umbraco-CMS/security/advisories/GHSA-77gj-crhp-3gvx
- https://nvd.nist.gov/vuln/detail/CVE-2024-43376
- https://github.com/umbraco/Umbraco-CMS/commit/b76070c794925932cb159ef50b851db6e966a004
- https://github.com/umbraco/Umbraco-CMS
