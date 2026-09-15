# [M] DNN: Same HostGUID for all new installs

## Summary
Severity: Medium
Advisory: GHSA-2rhw-gw3f-477j
CVE: CVE-2026-40306
CWE: CWE-330
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-04-10
Source: https://github.com/advisories/GHSA-2rhw-gw3f-477j
Type: github-advisory

## Affected
- NuGet: `DotNetNuke.Core` — affected >=10.0.0 <10.2.2

## Details
DNN (formerly DotNetNuke) is an open-source web content management platform (CMS) in the Microsoft ecosystem. All new installations of DNN 10.x.x - 10.2.1 have the same Host GUID. This does not affect upgrades from 9.x.x. Version 10.2.2 patches the issue.

## References
- https://github.com/dnnsoftware/Dnn.Platform/security/advisories/GHSA-2rhw-gw3f-477j
- https://nvd.nist.gov/vuln/detail/CVE-2026-40306
- https://github.com/dnnsoftware/Dnn.Platform
- https://github.com/dnnsoftware/Dnn.Platform/releases/tag/v10.2.2
