# [H] Microsoft.IdentityModel.Protocols.SignedHttpRequest remote code execution vulnerability

## Summary
Severity: High
Advisory: GHSA-rv9j-c866-gp5h
CVE: CVE-2024-21643
CWE: CWE-94
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2024-01-09
Source: https://github.com/advisories/GHSA-rv9j-c866-gp5h
Type: github-advisory

## Affected
- NuGet: `Microsoft.IdentityModel.Protocols.SignedHttpRequest` — affected >=0 <6.34.0
- NuGet: `Microsoft.IdentityModel.Protocols.SignedHttpRequest` — affected >=7.0.0-preview <7.1.2

## Details
### Impact
_What kind of vulnerability is it? Who is impacted?_
Anyone leveraging the `SignedHttpRequest`protocol or the `SignedHttpRequestValidator`is vulnerable. Microsoft.IdentityModel trusts the `jku`claim by default for the `SignedHttpRequest`protocol. This raises the possibility to make any remote or local `HTTP GET` request. 

### Patches
_Has the problem been patched? What versions should users upgrade to?_
The vulnerability has been fixed in Microsoft.IdentityModel.Protocols.SignedHttpRequest. Users **should** update **all** their Microsoft.IdentityModel versions to 7.1.2 (for 7x) or higher, 6.34.0 (for 6x) or higher, if using Microsoft.IdentityModel.Protocols.SignedHttpRequest.

### Workarounds
_Is there a way for users to fix or remediate the vulnerability without upgrading?_
No, users must upgrade.

### References
_Are there any links users can visit to find out more?_
https://aka.ms/IdentityModel/Jan2024/jku

## References
- https://github.com/AzureAD/azure-activedirectory-identitymodel-extensions-for-dotnet/security/advisories/GHSA-rv9j-c866-gp5h
- https://nvd.nist.gov/vuln/detail/CVE-2024-21643
- https://github.com/AzureAD/azure-activedirectory-identitymodel-extensions-for-dotnet
- https://github.com/AzureAD/azure-activedirectory-identitymodel-extensions-for-dotnet/releases/tag/6.34.0
- https://github.com/AzureAD/azure-activedirectory-identitymodel-extensions-for-dotnet/releases/tag/7.1.2
- https://github.com/AzureAD/azure-activedirectory-identitymodel-extensions-for-dotnet/wiki/jkucve
