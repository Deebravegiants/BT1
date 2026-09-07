# [C] .NET Core Remote Code Execution Vulnerability

## Summary
Severity: Critical
Advisory: GHSA-ghhp-997w-qr28
CVE: CVE-2021-26701
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-04-21
Source: https://github.com/advisories/GHSA-ghhp-997w-qr28
Type: github-advisory

## Affected
- NuGet: `System.Text.Encodings.Web` — affected >=4.0.0 <4.5.1
- NuGet: `System.Text.Encodings.Web` — affected >=4.6.0 <4.7.2
- NuGet: `System.Text.Encodings.Web` — affected >=5.0.0 <5.0.1

## Details
.NET Core Remote Code Execution Vulnerability This CVE ID is unique from CVE-2021-24112.

### Executive summary

Microsoft is releasing this security advisory to provide information about a vulnerability in .NET 5.0, .NET Core 3.1, and .NET Core 2.1. This advisory also provides guidance on what developers can do to update their applications to remove this vulnerability.

A remote code execution vulnerability exists in .NET 5 and .NET Core due to how text encoding is performed.

### Discussion

Discussion for this issue can be found at dotnet/runtime#49377

### Mitigation factors

Microsoft has not identified any mitigating factors for this vulnerability.

### Affected software

The vulnerable package is `System.Text.Encodings.Web` . Upgrading your package and redeploying your app should be sufficient to address this vulnerability.

Vulnerable package versions:

Any .NET 5, .NET Core, or .NET Framework based application that uses the System.Text.Encodings.Web package with a vulnerable version listed below.

Package Name | Vulnerable Versions | Secure Versions
-|-|-
System.Text.Encodings.Web | 4.0.0 - 4.5.0 | 4.5.1
System.Text.Encodings.Web |  4.6.0-4.7.1 | 4.7.2
System.Text.Encodings.Web | 5.0.0 |  5.0.1


Please validate that each of the .NET versions you are using is in support. Security updates are only provided for supported .NET versions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-26701
- https://github.com/dotnet/announcements/issues/178
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/S2AZOUKMCHT2WBHR7MYDTYXWOBHZW5P5
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TW3ZSJTTMZAFKGW7NJWTVVFZUYYU2SJZ
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UBOSSX7U6BSHV5RI74FCOW4ITJ5RRJR5
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WA5WQJVHUL5C4XMJTLY3C67R4WP35EF4
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/XPUKFHIGP5YNJRRFWKDJ2XRS4WTFJNNK
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YLFATXASXW4OV2ZBSRP4G55HJH73QPBP
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/S2AZOUKMCHT2WBHR7MYDTYXWOBHZW5P5
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/TW3ZSJTTMZAFKGW7NJWTVVFZUYYU2SJZ
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/UBOSSX7U6BSHV5RI74FCOW4ITJ5RRJR5
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/WA5WQJVHUL5C4XMJTLY3C67R4WP35EF4
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/XPUKFHIGP5YNJRRFWKDJ2XRS4WTFJNNK
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/YLFATXASXW4OV2ZBSRP4G55HJH73QPBP
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2021-26701
