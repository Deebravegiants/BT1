# [M] Exposure of Sensitive Information in OPC UA .NET Standard Reference Server

## Summary
Severity: Medium
Advisory: GHSA-4cvp-hr63-822j
CVE: CVE-2023-31048
CWE: CWE-200, CWE-209
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-05-05
Source: https://github.com/advisories/GHSA-4cvp-hr63-822j
Type: github-advisory

## Affected
- NuGet: `OPCFoundation.NetStandard.Opc.Ua.Core` — affected >=0 <1.4.371.86
- NuGet: `OPCFoundation.NetStandard.Opc.Ua.Server` — affected >=0 <1.4.371.86

## Details
This security update resolves a vulnerability in the OPC UA .NET Standard Reference Server that allows
remote attackers to send malicious requests that expose sensitive information.

https://files.opcfoundation.org/SecurityBulletins/OPC%20Foundation%20Security%20Bulletin%20CVE-2023-31048.pdf

## References
- https://github.com/OPCFoundation/UA-.NETStandard/security/advisories/GHSA-4cvp-hr63-822j
- https://nvd.nist.gov/vuln/detail/CVE-2023-31048
- https://files.opcfoundation.org/SecurityBulletins/OPC%20Foundation%20Security%20Bulletin%20CVE-2023-31048.pdf
- https://github.com/OPCFoundation/UA-.NETStandard
- https://github.com/OPCFoundation/UA-.NETStandard/releases
- https://github.com/OPCFoundation/UA-.NETStandard/releases/tag/1.4.371.86
