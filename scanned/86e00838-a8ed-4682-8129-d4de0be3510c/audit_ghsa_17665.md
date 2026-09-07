# [M] Umbraco CMS disclosure of configured password requirements 

## Summary
Severity: Medium
Advisory: GHSA-pgvc-6h2p-q4f6
CVE: CVE-2025-49147
CWE: CWE-497
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-06-24
Source: https://github.com/advisories/GHSA-pgvc-6h2p-q4f6
Type: github-advisory

## Affected
- NuGet: `Umbraco.Cms` — affected >=10.0.0 <10.8.11
- NuGet: `Umbraco.Cms` — affected >=13.0.0 <13.9.2

## Details
### Impact
Via a request to an anonymously authenticated endpoint it's possible to retrieve information about the configured password requirements.  The information available is limited but would perhaps give some additional detail useful for someone attempting to brute force derive a user's password.

The vulnerability can be found in the supported Umbraco versions 10 and 13.  It was not exposed in Umbraco 7 or 8, nor in 14 or higher versions.

### Patches
Patched in 10.8.11 and 13.9.2

## References
- https://github.com/umbraco/Umbraco-CMS/security/advisories/GHSA-pgvc-6h2p-q4f6
- https://nvd.nist.gov/vuln/detail/CVE-2025-49147
- https://github.com/umbraco/Umbraco-CMS/commit/b4144564c836ec6929111ce2a12eb1f67b42d61e
- https://github.com/umbraco/Umbraco-CMS/commit/d8f68d2c40f8e158bd81d469f25ef3a4e1d86c4c
- https://github.com/umbraco/Umbraco-CMS
