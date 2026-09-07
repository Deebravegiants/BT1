# [C] Deserialization of Untrusted Data in SinGooCMS.Utility

## Summary
Severity: Critical
Advisory: GHSA-29rv-fqx2-4c9f
CVE: CVE-2022-0749
CWE: CWE-502
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-03-18
Source: https://github.com/advisories/GHSA-29rv-fqx2-4c9f
Type: github-advisory

## Affected
- NuGet: `SinGooCMS.Utility` — affected >=0

## Details
This affects all versions of package SinGooCMS.Utility. The socket client in the package can pass in the payload via the user-controllable input after it has been established, because this socket client transmission does not have the appropriate restrictions or type bindings for the BinaryFormatter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-0749
- https://github.com/SinGooCMS/SinGooCMSUtility/issues/1
- https://github.com/SinGooCMS/SinGooCMSUtility/blob/master/SinGooCMS.Utility/Net/SocketClient.cs
- https://snyk.io/vuln/SNYK-DOTNET-SINGOOCMSUTILITY-2312979
