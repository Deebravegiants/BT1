# [M] DNN vulnerable to Relative Path Traversal

## Summary
Severity: Medium
Advisory: GHSA-9w72-2f23-57gm
CVE: CVE-2022-2922
CWE: CWE-22, CWE-23
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-10-01
Source: https://github.com/advisories/GHSA-9w72-2f23-57gm
Type: github-advisory

## Affected
- NuGet: `DotNetNuke.Core` — affected >=0 <9.11.0
- NuGet: `DotNetNuke.Web` — affected >=0 <9.11.0

## Details
DNN (GitHub repository dnnsoftware/dnn.platform) prior to 9.11.0 is vulnerable to Relative Path Traversal. Version 9.11.0 contains a patch for this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-2922
- https://github.com/dnnsoftware/Dnn.Platform/commit/3697c5344cef8d49214230f0cc2efcd9e93a00a8
- https://github.com/dnnsoftware/dnn.platform/commit/9b17351592fbde376506ba6705dbcc7a74a2a195
- https://github.com/dnnsoftware/dnn.platform
- https://huntr.dev/bounties/74918f40-dc11-4218-abef-064eb71a0703
