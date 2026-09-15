# [H] Path traversal in elFinder.NetCore

## Summary
Severity: High
Advisory: GHSA-9rjp-r58j-fxgq
CVE: CVE-2021-23428
CWE: CWE-20, CWE-22
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2021-09-02
Source: https://github.com/advisories/GHSA-9rjp-r58j-fxgq
Type: github-advisory

## Affected
- NuGet: `elFinder.NetCore` — affected >=0

## Details
This affects all versions of package elFinder.NetCore. The Path.Combine(...) method is used to create an absolute file path. Due to missing sanitation of the user input and a missing check of the generated path its possible to escape the Files directory via path traversal

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23428
- https://github.com/gordon-matt/elFinder.NetCore
- https://github.com/gordon-matt/elFinder.NetCore/blob/633da9a4d7d5c9baefd1730ee51bf7af54889600/elFinder.NetCore/Drivers/FileSystem/FileSystemDriver.cs#L387
- https://github.com/gordon-matt/elFinder.NetCore/blob/633da9a4d7d5c9baefd1730ee51bf7af54889600/elFinder.NetCore/Drivers/FileSystem/FileSystemDriver.cs%23L387
- https://snyk.io/vuln/SNYK-DOTNET-ELFINDERNETCORE-1313838
