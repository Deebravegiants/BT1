# [M] DNN: Force Friend Request Acceptance

## Summary
Severity: Medium
Advisory: GHSA-fpj4-9qhx-5m6m
CVE: CVE-2026-40305
CWE: CWE-285
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-04-10
Source: https://github.com/advisories/GHSA-fpj4-9qhx-5m6m
Type: github-advisory

## Affected
- NuGet: `DotNetNuke.Core` — affected >=6.0.0 <10.2.2

## Details
DNN (formerly DotNetNuke) is an open-source web content management platform (CMS) in the Microsoft ecosystem. Starting in version 6.0.0 and prior to version 10.2.2, in the friends feature, a user could craft a request that would force the acceptance of a friend request on another user. Version 10.2.2 patches the issue.

## References
- https://github.com/dnnsoftware/Dnn.Platform/security/advisories/GHSA-fpj4-9qhx-5m6m
- https://nvd.nist.gov/vuln/detail/CVE-2026-40305
- https://github.com/dnnsoftware/Dnn.Platform
- https://github.com/dnnsoftware/Dnn.Platform/releases/tag/v10.2.2
