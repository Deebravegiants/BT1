# [M] Reflected Cross-Site Scripting (XSS) in module actions in edit mode

## Summary
Severity: Medium
Advisory: GHSA-79m3-rvx2-3qq9
CVE: CVE-2025-48377
CWE: CWE-79
Ecosystem: NuGet
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:A/VC:N/VI:N/VA:N/SC:H/SI:N/SA:N (CVSS_V4)
Published: 2025-05-23
Source: https://github.com/advisories/GHSA-79m3-rvx2-3qq9
Type: github-advisory

## Affected
- NuGet: `DotNetNuke.Web` — affected >=0 <9.13.9
- NuGet: `DotNetNuke.Core` — affected >=0 <9.13.9

## Details
A specially crafted URL may be constructed which can inject an XSS payload that is triggered by using some module actions.

## References
- https://github.com/dnnsoftware/Dnn.Platform/security/advisories/GHSA-79m3-rvx2-3qq9
- https://nvd.nist.gov/vuln/detail/CVE-2025-48377
- https://github.com/dnnsoftware/Dnn.Platform/commit/351b166492ad4b6509c273dc83211d52238e31a7
- https://github.com/dnnsoftware/Dnn.Platform
