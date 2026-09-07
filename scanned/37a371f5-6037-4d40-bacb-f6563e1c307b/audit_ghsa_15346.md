# [M] Umbraco CMS Improper Access Control vulnerability

## Summary
Severity: Medium
Advisory: GHSA-hrww-x3fq-xcvh
CVE: CVE-2024-43377
CWE: CWE-284
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-08-20
Source: https://github.com/advisories/GHSA-hrww-x3fq-xcvh
Type: github-advisory

## Affected
- NuGet: `Umbraco.Cms` — affected >=14.0.0 <14.1.2

## Details
### Impact
As an authenticated user one can access a few unintended endpoints

### Explanation of the vulnerability
Few endpoints in Umbraco Management API was not protected by a specific section. These just required you to be authenticated. Due to the fact that a member is also just authenticated, it was possible to get info from these endpoints using a member token.

## References
- https://github.com/umbraco/Umbraco-CMS/security/advisories/GHSA-hrww-x3fq-xcvh
- https://nvd.nist.gov/vuln/detail/CVE-2024-43377
- https://github.com/umbraco/Umbraco-CMS/commit/72bef8861d94a39d5cc9530a04c4797b91fcbecf
- https://github.com/umbraco/Umbraco-CMS
