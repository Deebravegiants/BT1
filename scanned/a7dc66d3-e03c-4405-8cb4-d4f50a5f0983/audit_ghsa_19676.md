# [H] Microsoft Security Advisory CVE-2025-24043 | WinDbg Remote Code Execution Vulnerability

## Summary
Severity: High
Advisory: GHSA-hpw7-8qpc-34p3
CVE: CVE-2025-24043
CWE: CWE-347
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-03-07
Source: https://github.com/advisories/GHSA-hpw7-8qpc-34p3
Type: github-advisory

## Affected
- NuGet: `dotnet-sos` — affected >=0 <9.0.607501
- NuGet: `dotnet-dump` — affected >=0 <9.0.607501
- NuGet: `dotnet-debugger-extensions` — affected >=0 <9.0.607601

## Details
# Microsoft Security Advisory CVE-2025-24043 | WinDbg Remote Code Execution Vulnerability

## <a name="executive-summary"></a>Executive summary

Microsoft is releasing this security advisory to provide information about a vulnerability in [WinDbg](https://aka.ms/windbg/download). This advisory also provides guidance on what developers can do to update their applications to remove this vulnerability.

Improper verification of cryptographic signature in SOS allows an authorized attacker to execute code over a network resulting in Remote Code Execution.

## Announcement

Announcement for this issue can be found at  https://github.com/dotnet/announcements/issues/346

## <a name="mitigation-factors"></a>Mitigation factors

Microsoft has not identified any mitigating factors for this vulnerability.

## <a name="affected-packages"></a>Affected Packages
The vulnerability affects any Microsoft .NET Core project if it uses any of affected packages versions listed below

### <a name="">WinDbg</a> WinDbg
Package name | Affected version | Patched version
------------ | ---------------- | -------------------------
[dotnet-sos](https://www.nuget.org/packages/dotnet-sos) | < 9.0.607501 | 9.0.607501
[dotnet-dump](https://www.nuget.org/packages/dotnet-dump) | < 9.0.557512 | 9.0.607501
[dotnet-debugger-extensions](https://www.nuget.org/packages/dotnet-debugger-extensions) | 9.0.557512 | 9.0.607601

## Advisory FAQ

### <a name="how-affected"></a>How do I know if I am affected?

If you you are using the affected version listed in [affected packages](#affected-software), you're exposed to the vulnerability.

### <a name="how-fix"></a>How do I fix the issue?

1. To fix the issue please install the latest version of [WinDbg](https://aka.ms/windbg/download).
2. If your application references the vulnerable package, update the package reference to the patched version.

## Other Information

### Reporting Security Issues

If you have found a potential security issue, please email details to secure@microsoft.com. Reports may qualify for the Microsoft .NET Core & .NET 5 Bounty. Details of the Microsoft .NET Bounty Program including terms and conditions are at <https://aka.ms/corebounty>.

### Support

You can ask questions about this issue on GitHub in the .NET GitHub organization. 

### Disclaimer

The information provided in this advisory is provided "as is" without warranty of any kind. Microsoft disclaims all warranties, either express or implied, including the warranties of merchantability and fitness for a particular purpose. In no event shall Microsoft Corporation or its suppliers be liable for any damages whatsoever including direct, indirect, incidental, consequential, loss of business profits or special damages, even if Microsoft Corporation or its suppliers have been advised of the possibility of such damages. Some states do not allow the exclusion or limitation of liability for consequential or incidental damages so the foregoing limitation may not apply.

### External Links

[CVE-2025-24043]( https://www.cve.org/CVERecord?id=CVE-2025-24043)

### Revisions

V1.0 (March 06, 2024): Advisory published.

_Version 1.0_

_Last Updated 2025-03-06_

## References
- https://github.com/dotnet/diagnostics/security/advisories/GHSA-hpw7-8qpc-34p3
- https://nvd.nist.gov/vuln/detail/CVE-2025-24043
- https://github.com/dotnet/diagnostics
- https://github.com/dotnet/diagnostics/releases/tag/v9.0.607501
- https://msrc.microsoft.com/update-guide/vulnerability/CVE-2025-24043
