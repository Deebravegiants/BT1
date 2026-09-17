# [M] Security Update for the OPC UA .NET Standard Stack

## Summary
Severity: Medium
Advisory: GHSA-7vfh-cqpc-4267
CVE: CVE-2024-45526
CWE: CWE-770
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2024-10-18
Source: https://github.com/advisories/GHSA-7vfh-cqpc-4267
Type: github-advisory

## Affected
- NuGet: `OPCFoundation.NetStandard.Opc.Ua` — affected >=0 <1.5.374.118
- NuGet: `OPCFoundation.NetStandard.Opc.Ua.Core` — affected >=0 <1.5.374.118

## Details
This security update resolves a vulnerability in the OPC UA .NET Standard Stack that allows an
unauthorized attacker to trigger a gradual degradation in performance.

## References
- https://github.com/OPCFoundation/UA-.NETStandard/security/advisories/GHSA-7vfh-cqpc-4267
- https://nvd.nist.gov/vuln/detail/CVE-2024-45526
- https://files.opcfoundation.org/SecurityBulletins/OPC%20Foundation%20Security%20Bulletin%20CVE-2024-45526.pdf
- https://github.com/OPCFoundation/UA-.NETStandard
