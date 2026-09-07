# [H] idunno.Bluesky, idunno.AtProto and idunno.AtProto.OAuthCallback Denial of Service Vulnerability

## Summary
Severity: High
Advisory: GHSA-8fh9-c4jq-94h4
CWE: CWE-129
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-13
Source: https://github.com/advisories/GHSA-8fh9-c4jq-94h4
Type: github-advisory

## Affected
- NuGet: `idunno.AtProto` — affected >=0 <1.7.0
- NuGet: `idunno.AtProto.OAuthCallback` — affected >=0 <1.7.0
- NuGet: `idunno.Bluesky` — affected >=0 <1.7.0

## Details
# idunno.Bluesky, idunno.AtProto and idunno.AtProto.OAuthCallback Denial of Service Vulnerability

## Impact

The `Microsoft.Bcl.Memory` package, a transitive dependency of `idunno.AtProto` and `idunno.AtProto.OAuthCallback` had a Denial of Service security vulnerability, [CVE-2026-26127](https://github.com/dotnet/announcements/issues/384)

## Patches

v1.7.0 updates the dependencies on `Duende.IdentityModel.OidcClient` and `Duende.IdentityModel.OidcClient.Extensions` which, in turn, updates their dependency on `Microsoft.Bcl.Memory` to 10.0.4, resolving the vulnerability.

## Workarounds

No workarounds exist for this vulnerability.

## How to fix the issue

To update your dependencies on `idunno.Bluesky`, `idunno.AtProto` and `idunno.AtProto.OAuthCallback`, 

### Using the .NET CLI (Command Line Interface):

* Open a terminal or command prompt in your project's directory.
* To update a specific package to its latest version, use the following add package command:
   
  * If you are using `idunno.Bluesky`
    `dotnet package update idunno.Bluesky`

  * If you are using `idunno.AtProto` as a direct dependency
    `dotnet package update idunno.AtProto`

  * If you are using `idunno.AtProto.OAuthCallback` as a direct dependency
    `dotnet package update idunno.AtProto.OAuthCallback`

### Using the NuGet Package Manager Console in Visual Studio:

* Open your project in Visual Studio.
* Navigate to "Tools > NuGet Package Manager > Package Manager Console".
* To update a specific package to its latest version, use the following Update-Package command:

  * If you are using `idunno.Bluesky`
    `Update-Package -Id idunno.Bluesky`

  * If you are using `idunno.AtProto` as a direct dependency
    `Update-Package -Id idunno.AtProto`

  * If you are using `idunno.AtProto.OAuthCallback` as a direct dependency
    `Update-Package -Id idunno.AtProto.OAuthCallback`

### NuGet Package Manager UI in Visual Studio:

* Open your project in Visual Studio.
* Right-click on your project in Solution Explorer and select "Manage NuGet Packages..." or navigate to "Project > Manage NuGet Packages".
* In the NuGet Package Manager window, select the "Updates" tab. This tab lists packages with available updates from your configured package sources.
* Select the package(s) you wish to update. You can choose a specific version from the dropdown or update to the latest available version.
* Click the "Update" button.

## References

*  [Microsoft Security Advisory CVE-2026-26127 – .NET Denial of Service Vulnerability](https://github.com/dotnet/announcements/issues/384)
*  [CVE-2026-26127](https://www.cve.org/CVERecord?id=CVE-2026-26127)

## References
- https://github.com/blowdart/idunno.Bluesky/security/advisories/GHSA-8fh9-c4jq-94h4
- https://github.com/dotnet/announcements/issues/384
- https://github.com/blowdart/idunno.Bluesky
- https://www.cve.org/CVERecord?id=CVE-2026-26127
