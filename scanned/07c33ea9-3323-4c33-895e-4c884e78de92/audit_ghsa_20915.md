# [C] Orckestra C1 CMS's deserialization of untrusted data allows for arbitrary code execution.

## Summary
Severity: Critical
Advisory: GHSA-gfhp-jgp6-838j
CVE: CVE-2022-39256
CWE: CWE-502
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2022-09-30
Source: https://github.com/advisories/GHSA-gfhp-jgp6-838j
Type: github-advisory

## Affected
- NuGet: `CompositeC1.Core` — affected >=0 <6.13

## Details
### Impact

This vulnerability allows remote attackers to execute arbitrary code on affected installations of Orckestra C1 CMS. 
Authentication is required to exploit this vulnerability.
The authenticated user may perform the actions unknowingly by visiting a specially crafted site.

### Patches
Patched in C1 CMS v6.13

### Workarounds
Upgrade to C1 CMS v6.13 or newer is required

### Credit
This issue was discovered and reported by Markus Wulftange  / [Code White GmbH](https://code-white.com/en/).

## References
- https://github.com/Orckestra/C1-CMS-Foundation/security/advisories/GHSA-gfhp-jgp6-838j
- https://nvd.nist.gov/vuln/detail/CVE-2022-39256
- https://github.com/Orckestra/C1-CMS-Foundation/pull/814
- https://github.com/Orckestra/C1-CMS-Foundation/commit/af856ab5a62d19acf6aea1b1f4c6c3c4985c9446
- https://github.com/Orckestra/C1-CMS-Foundation
- https://github.com/Orckestra/C1-CMS-Foundation/releases/tag/v6.13
