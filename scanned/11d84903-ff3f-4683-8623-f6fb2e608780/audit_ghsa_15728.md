# [H] OPCFoundation.NetStandard.Opc.Ua.Core buffer-management vulnerability

## Summary
Severity: High
Advisory: GHSA-4q2p-hwmr-qcxc
CVE: CVE-2024-33862
CWE: CWE-770
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-07-06
Source: https://github.com/advisories/GHSA-4q2p-hwmr-qcxc
Type: github-advisory

## Affected
- NuGet: `OPCFoundation.NetStandard.Opc.Ua.Core` — affected >=0 <1.5.374.54

## Details
A buffer-management vulnerability in OPC Foundation OPCFoundation.NetStandard.Opc.Ua.Core before 1.5.374.54 could allow remote attackers to exhaust memory resources. It is triggered when the system receives an excessive number of messages from a remote source. This could potentially lead to a denial of service (DoS) condition, disrupting the normal operation of the system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-33862
- https://github.com/OPCFoundation/UA-.NETStandard/commit/52d4492ccc928f128e7a38857fdf58d94e1e652b
- https://files.opcfoundation.org/SecurityBulletins/OPC%20Foundation%20Security%20Bulletin%20CVE-2024-33862.pdf
- https://github.com/OPCFoundation/UA-.NETStandard
- https://github.com/OPCFoundation/UA-.NETStandard/releases/tag/1.5.374.54
