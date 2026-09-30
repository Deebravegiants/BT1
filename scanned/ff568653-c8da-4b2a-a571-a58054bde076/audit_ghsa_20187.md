# [H] Incorrect Implementation of Authentication Algorithm in OPCFoundation.NetStandard.Opc.Ua.Core

## Summary
Severity: High
Advisory: GHSA-fvxf-r9fw-49pc
CVE: CVE-2022-29865
CWE: CWE-287
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-06-17
Source: https://github.com/advisories/GHSA-fvxf-r9fw-49pc
Type: github-advisory

## Affected
- NuGet: `OPCFoundation.NetStandard.Opc.Ua.Core` — affected >=0 <1.4.368.58

## Details
A vulnerability was discovered in the OPC UA .NET Standard Stack that
-  allows a malicious client or server to bypass the application authentication mechanism
-  and allow a connection to an untrusted peer.

## References
- https://github.com/OPCFoundation/UA-.NETStandard/security/advisories/GHSA-fvxf-r9fw-49pc
- https://nvd.nist.gov/vuln/detail/CVE-2022-29865
- https://files.opcfoundation.org/SecurityBulletins/OPC%20Foundation%20Security%20Bulletin%20CVE-2022-29865.pdf
- https://github.com/OPCFoundation/UA-.NETStandard
- https://opcfoundation.org/security
