# [M] OPC UA applications can allow a remote attacker to determine a Server's private key 

## Summary
Severity: Medium
Advisory: GHSA-gr4c-5rq6-cgh3
CVE: CVE-2018-7559
Ecosystem: NuGet
CVSS: CVSS:3.0/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2018-10-16
Source: https://github.com/advisories/GHSA-gr4c-5rq6-cgh3
Type: github-advisory

## Affected
- NuGet: `OPCFoundation.NetStandard.Opc.Ua` — affected >=0 <1.3.352.12

## Details
An issue was discovered in OPC UA .NET Standard Stack and Sample Code before GitHub commit 2018-04-12, and OPC UA .NET Legacy Stack and Sample Code before GitHub commit 2018-03-13. A vulnerability in OPC UA applications can allow a remote attacker to determine a Server's private key by sending carefully constructed bad UserIdentityTokens as part of an oracle attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-7559
- https://github.com/OPCFoundation/UA-.NET-Legacy/commit/e2a781b38efb8686d2bd850c2f2372b5c670bc45
- https://github.com/OPCFoundation/UA-.NETStandard/commit/ebcf026a54dd0c9052cff009d96d827ac923d150
- https://github.com/OPCFoundation/UA-.NETStandard
- https://github.com/advisories/GHSA-gr4c-5rq6-cgh3
- https://opcfoundation-onlineapplications.org/faq/SecurityBulletins/OPC_Foundation_Security_Bulletin_CVE-2018-7559.pdf
- http://www.securityfocus.com/bid/108688
