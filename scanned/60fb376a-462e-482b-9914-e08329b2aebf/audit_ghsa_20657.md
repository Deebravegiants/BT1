# [M] Exposure of Sensitive Information in OPCFoundation.NetStandard.Opc.Ua.Server

## Summary
Severity: Medium
Advisory: GHSA-mw9h-hcp7-fgc6
CVE: CVE-2022-33916
CWE: CWE-200
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-08-24
Source: https://github.com/advisories/GHSA-mw9h-hcp7-fgc6
Type: github-advisory

## Affected
- NuGet: `OPCFoundation.NetStandard.Opc.Ua.Server` — affected >=0 <1.4.370.9

## Details
OPC UA .NET Standard Reference Server 1.04.368 allows a remote attacker to cause the application to access sensitive information.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-33916
- https://github.com/OPCFoundation/UA-.NETStandard/commit/313aa2a2499d8690cf719a67176e131517bb8b78
- https://files.opcfoundation.org/SecurityBulletins/OPC%20Foundation%20Security%20Bulletin%20CVE-2022-33916.pdf
- https://github.com/OPCFoundation/UA-.NETStandard
