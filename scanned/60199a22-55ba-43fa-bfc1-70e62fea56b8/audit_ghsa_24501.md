# [H] Remote code execution in Microsoft.WindowsDesktop.App.Ref

## Summary
Severity: High
Advisory: GHSA-r4mw-gxf7-vxr9
CVE: CVE-2020-0606
CWE: CWE-20
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-r4mw-gxf7-vxr9
Type: github-advisory

## Affected
- NuGet: `Microsoft.WindowsDesktop.App.Ref` — affected >=3.0.1 <3.0.2
- NuGet: `Microsoft.WindowsDesktop.App.Ref` — affected >=3.1.0 <3.1.1
- NuGet: `Microsoft.WindowsDesktop.App.Runtime.win-x86` — affected >=3.0.0 <3.0.2
- NuGet: `Microsoft.WindowsDesktop.App.Runtime.win-x86` — affected >=3.1.0 <3.1.11
- NuGet: `Microsoft.WindowsDesktop.App.Runtime.win-x64` — affected >=3.0.0 <3.0.2
- NuGet: `Microsoft.WindowsDesktop.App.Runtime.win-x64` — affected >=3.1.0 <3.1.11

## Details
A remote code execution vulnerability exists in .NET software when the software fails to check the source markup of a file.An attacker who successfully exploited the vulnerability could run arbitrary code in the context of the current user, aka '.NET Framework Remote Code Execution Vulnerability'. This CVE ID is unique from CVE-2020-0605.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-0606
- https://github.com/dotnet/announcements/issues/149
- https://github.com/github/advisory-database/issues/302
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2020-0606
