# [M] Azure SDK for .NET Information Disclosure Vulnerability.

## Summary
Severity: Medium
Advisory: GHSA-whph-446h-6m9v
CVE: CVE-2022-26907
CWE: CWE-532
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-04-16
Source: https://github.com/advisories/GHSA-whph-446h-6m9v
Type: github-advisory

## Affected
- NuGet: `Microsoft.Rest.ClientRuntime` — affected >=0 <2.3.24

## Details
Azure SDK for .NET Information Disclosure Vulnerability via undisclosed methods relating to lack of sanitization of exception messages.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-26907
- https://github.com/Azure/azure-sdk-for-net/pull/28169
- https://github.com/Azure/azure-sdk-for-net/commit/e67f2a9fc5aa1060bd465d1458c347671268f6f5
- https://github.com/Azure/azure-sdk-for-net
- https://github.com/Azure/azure-sdk-for-net/blob/a919c48ae294fed084a9679b6f53ac6af3fb4c3a/sdk/mgmtcommon/ClientRuntime/ClientRuntime/Microsoft.Rest.ClientRuntime.csproj#L11
- https://msrc.microsoft.com/update-guide/vulnerability/CVE-2022-26907
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2022-26907
