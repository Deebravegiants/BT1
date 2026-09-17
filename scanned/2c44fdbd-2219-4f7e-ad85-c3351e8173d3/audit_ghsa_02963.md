# [M] Improper Certificate Validation in OPCFoundation.NetStandard.Opc.Ua.Core

## Summary
Severity: Medium
Advisory: GHSA-mjww-934m-h4jw
CVE: CVE-2020-29457
CWE: CWE-295
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2021-11-19
Source: https://github.com/advisories/GHSA-mjww-934m-h4jw
Type: github-advisory

## Affected
- NuGet: `OPCFoundation.NetStandard.Opc.Ua.Core` — affected >=0 <1.4.365.10

## Details
A Privilege Elevation vulnerability in OPC UA .NET Standard Stack 1.4.363.107 allows attackers to establish a connection using invalid certificates.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-29457
- https://github.com/OPCFoundation/UA-.NETStandard/pull/1229
- https://github.com/OPCFoundation/UA-.NETStandard/pull/1229/commits/d815cfb972bd668c1b6e461f6ff97519d6b26f25
- https://github.com/OPCFoundation/UA-.NETStandard
- https://opcfoundation.org/SecurityBulletins/OPC%20Foundation%20Security%20Bulletin%20CVE-2020-29457.pdf
- https://www.nuget.org/packages/OPCFoundation.NetStandard.Opc.Ua
