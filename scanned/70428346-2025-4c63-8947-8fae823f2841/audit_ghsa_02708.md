# [C] Imporoper path validation in elFinder.NetCore

## Summary
Severity: Critical
Advisory: GHSA-wmpm-fq7r-jq56
CVE: CVE-2021-23427
CWE: CWE-20
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-09-02
Source: https://github.com/advisories/GHSA-wmpm-fq7r-jq56
Type: github-advisory

## Affected
- NuGet: `elFinder.NetCore` — affected >=0

## Details
This affects all versions of package elFinder.NetCore. The ExtractAsync function within the FileSystem is vulnerable to arbitrary extraction due to insufficient validation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23427
- https://github.com/gordon-matt/elFinder.NetCore
- https://github.com/gordon-matt/elFinder.NetCore/blob/633da9a4d7d5c9baefd1730ee51bf7af54889600/elFinder.NetCore/Drivers/FileSystem/FileSystemDriver.cs#L226
- https://github.com/gordon-matt/elFinder.NetCore/blob/633da9a4d7d5c9baefd1730ee51bf7af54889600/elFinder.NetCore/Drivers/FileSystem/FileSystemDriver.cs%23L226
- https://snyk.io/vuln/SNYK-DOTNET-ELFINDERNETCORE-1567778
