# [M] Umbraco Makes User Enumeration Feasible Based on Timing of Login Response

## Summary
Severity: Medium
Advisory: GHSA-4g8m-5mj5-c8xg
CVE: CVE-2025-46736
CWE: CWE-204
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-05-06
Source: https://github.com/advisories/GHSA-4g8m-5mj5-c8xg
Type: github-advisory

## Affected
- NuGet: `Umbraco.Cms` — affected >=11.0.0-rc1 <13.8.1
- NuGet: `Umbraco.Cms` — affected >=0 <10.8.10

## Details
### Impact
Based on an analysis of the timing of post login API responses, it's possible to determine whether an account exists.

### Patches
Patched in 10.8.10 and 13.8.1.

### Workarounds
None available.

## References
- https://github.com/umbraco/Umbraco-CMS/security/advisories/GHSA-4g8m-5mj5-c8xg
- https://nvd.nist.gov/vuln/detail/CVE-2025-46736
- https://github.com/umbraco/Umbraco-CMS/commit/14fbd20665b453cbf094ccf4575b79a9fba07e03
- https://github.com/umbraco/Umbraco-CMS/commit/34709be6cce9752dfa767dffbf551305f48839bc
- https://github.com/umbraco/Umbraco-CMS
