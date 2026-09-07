# [H] Vulnerability in Azure Active Directory Authentication Library

## Summary
Severity: High
Advisory: GHSA-xc6x-cq47-9chw
CVE: CVE-2019-1258
Ecosystem: NuGet
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-08-16
Source: https://github.com/advisories/GHSA-xc6x-cq47-9chw
Type: github-advisory

## Affected
- NuGet: `microsoft.identitymodel.clients.activedirectory` — affected >=5.0.0 <5.2.0

## Details
An elevation of privilege vulnerability exists in Azure Active Directory Authentication Library On-Behalf-Of flow, in the way the library caches tokens, aka 'Azure Active Directory Authentication Library Elevation of Privilege Vulnerability'.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-1258
- https://github.com/AzureAD/azure-activedirectory-library-for-dotnet
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2019-1258
