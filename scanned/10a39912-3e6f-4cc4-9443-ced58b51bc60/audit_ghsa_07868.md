# [C] Semantic Kernel has Arbitrary File Write via AI Agent Function Calling in .NET SDK

## Summary
Severity: Critical
Advisory: GHSA-2ww3-72rp-wpp4
CVE: CVE-2026-25592
CWE: CWE-22
Ecosystem: NuGet, PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-02-06
Source: https://github.com/advisories/GHSA-2ww3-72rp-wpp4
Type: github-advisory

## Affected
- PyPI: `semantic-kernel` — affected >=0 <1.39.3
- NuGet: `Microsoft.SemanticKernel.Core` — affected >=0 <1.71.0

## Details
### Impact
_What kind of vulnerability is it? Who is impacted?_
An Arbitrary File Write vulnerability has been identified in Microsoft's Semantic Kernel .NET SDK, specifically within the `SessionsPythonPlugin`.
Developers who have built applications which include Microsoft's Semantic Kernel .NET SDK and are using the `SessionsPythonPlugin`

### Patches
_Has the problem been patched? What versions should users upgrade to?_
The problem has been fixed in [Microsoft.SemanticKernel.Plugins.Core version 1.71.0](https://www.nuget.org/packages/Microsoft.SemanticKernel.Plugins.Core/1.71.0). Users should upgrade to version 1.71.0 or higher.

### Workarounds
_Is there a way for users to fix or remediate the vulnerability without upgrading?_
Users can create a [Function Invocation Filter](https://learn.microsoft.com/en-us/semantic-kernel/concepts/enterprise-readiness/filters?pivots=programming-language-csharp#function-invocation-filter) which checks the arguments being passed to any calls to `DownloadFileAsync ` or `UploadFileAsync` and ensures the provided `localFilePath` is allow listed.

### References
_Are there any links users can visit to find out more?_
- [Sample showing safe use of the CodeInterpreterPlugin](https://github.com/microsoft/semantic-kernel/blob/main/dotnet/samples/Demos/CodeInterpreterPlugin/Program.cs#L61-L64)
- [PR to Add file upload security controls to SessionsPythonPlugin](https://github.com/microsoft/semantic-kernel/pull/13478/changes#diff-88d3cacba2bfa84eef8f2aa171b34f9940338cbb784a3ffc49f5fe3af1b8943d)

## References
- https://github.com/microsoft/semantic-kernel/security/advisories/GHSA-2ww3-72rp-wpp4
- https://nvd.nist.gov/vuln/detail/CVE-2026-25592
- https://github.com/microsoft/semantic-kernel/pull/13478/changes#diff-88d3cacba2bfa84eef8f2aa171b34f9940338cbb784a3ffc49f5fe3af1b8943d
- https://github.com/microsoft/semantic-kernel
- https://github.com/microsoft/semantic-kernel/blob/main/dotnet/samples/Demos/CodeInterpreterPlugin/Program.cs#L61-L64
