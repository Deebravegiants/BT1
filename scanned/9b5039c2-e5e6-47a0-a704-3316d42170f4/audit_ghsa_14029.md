# [H] Uncontrolled Resource Consumption in OPC UA .NET Standard Reference Server

## Summary
Severity: High
Advisory: GHSA-vpf7-r2fv-75m9
CVE: CVE-2023-27321
CWE: CWE-400
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-05-05
Source: https://github.com/advisories/GHSA-vpf7-r2fv-75m9
Type: github-advisory

## Affected
- NuGet: `OPCFoundation.NetStandard.Opc.Ua.Server` — affected >=0 <1.4.371.86

## Details
This security update resolves a vulnerability in the OPC UA .NET Standard Reference Server that allows
remote attackers to send malicious requests that consume all memory available to the server.

https://files.opcfoundation.org/SecurityBulletins/OPC%20Foundation%20Security%20Bulletin%20CVE-2023-27321.pdf

## References
- https://github.com/OPCFoundation/UA-.NETStandard/security/advisories/GHSA-vpf7-r2fv-75m9
- https://nvd.nist.gov/vuln/detail/CVE-2023-27321
- https://files.opcfoundation.org/SecurityBulletins/OPC%20Foundation%20Security%20Bulletin%20CVE-2023-27321.pdf
- https://github.com/OPCFoundation/UA-.NETStandard
- https://www.zerodayinitiative.com/advisories/ZDI-23-548
