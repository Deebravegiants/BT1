# [M] Umbraco Allows User Enumeration Feasible Based On Management API Timing and Response Codes 

## Summary
Severity: Medium
Advisory: GHSA-hmg4-wwm5-p999
CVE: CVE-2025-24011
CWE: CWE-200, CWE-203
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-01-21
Source: https://github.com/advisories/GHSA-hmg4-wwm5-p999
Type: github-advisory

## Affected
- NuGet: `Umbraco.Cms` — affected >=14.0.0 <14.3.2
- NuGet: `Umbraco.Cms` — affected >=15.0.0 <15.1.2

## Details
### Impact

Based on an analysis of response codes and timing of Umbraco 14+ management API responses, it's possible to determine whether an account exists.

### Patches

Patched in 14.3.2 and 15.1.2.

### Workarounds

None available.

## References
- https://github.com/umbraco/Umbraco-CMS/security/advisories/GHSA-hmg4-wwm5-p999
- https://nvd.nist.gov/vuln/detail/CVE-2025-24011
- https://github.com/umbraco/Umbraco-CMS/commit/559c6c9f312df1d6eb1bde82c4b81c0896da6382
- https://github.com/umbraco/Umbraco-CMS/commit/839b6816f2ae3e5f54459a0f09dad6b17e2d1e07
- https://github.com/umbraco/Umbraco-CMS
