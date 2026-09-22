# [M] Insufficient Session Expiration and TOCTOU Race Condition in OPC FOundation UA .Net Standard

## Summary
Severity: Medium
Advisory: GHSA-9q94-v7ch-mxqw
CVE: CVE-2020-8867
CWE: CWE-367, CWE-613
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-02
Source: https://github.com/advisories/GHSA-9q94-v7ch-mxqw
Type: github-advisory

## Affected
- NuGet: `OPCFoundation.NetStandard.Opc.Ua` — affected >=0 <1.4.359.31

## Details
This vulnerability allows remote attackers to create a denial-of-service condition on affected installations of OPC Foundation UA .NET Standard 1.04.358.30. Authentication is not required to exploit this vulnerability. The specific flaw exists within the handling of sessions. The issue results from the lack of proper locking when performing operations on an object. An attacker can leverage this vulnerability to create a denial-of-service condition against the application. Was ZDI-CAN-10295.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-8867
- https://github.com/OPCFoundation/UA-.NETStandard/releases/tag/1.4.359.31
- https://opcfoundation.org/SecurityBulletins/OPC%20Foundation%20Security%20Bulletin%20CVE-2020-8867.pdf
- https://www.zerodayinitiative.com/advisories/ZDI-20-536
