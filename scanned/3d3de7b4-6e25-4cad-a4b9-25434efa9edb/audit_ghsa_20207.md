# [H] Uncontrolled Resource Consumption in OPCFoundation.NetStandard.Opc.Ua.Core

## Summary
Severity: High
Advisory: GHSA-vhfw-v69p-crcw
CVE: CVE-2022-29864
CWE: CWE-400
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-06-17
Source: https://github.com/advisories/GHSA-vhfw-v69p-crcw
Type: github-advisory

## Affected
- NuGet: `OPCFoundation.NetStandard.Opc.Ua.Core` — affected >=0 <1.4.368.58

## Details
A vulnerability was discovered in the OPC UA .NET Standard Stack that allows a malicious client to cause a server to trigger an out of memory exception by sending a large number of message chunks.

## References
- https://github.com/OPCFoundation/UA-.NETStandard/security/advisories/GHSA-vhfw-v69p-crcw
- https://nvd.nist.gov/vuln/detail/CVE-2022-29864
- https://files.opcfoundation.org/SecurityBulletins/OPC%20Foundation%20Security%20Bulletin%20CVE-2022-29864.pdf
- https://github.com/OPCFoundation/UA-.NETStandard
