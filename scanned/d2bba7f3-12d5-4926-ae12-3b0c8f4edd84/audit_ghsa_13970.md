# [H] MongoDB .NET/C# Driver vulnerable to Deserialization of Untrusted Data

## Summary
Severity: High
Advisory: GHSA-7j9m-j397-g4wx
CVE: CVE-2022-48282
CWE: CWE-502
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-02-21
Source: https://github.com/advisories/GHSA-7j9m-j397-g4wx
Type: github-advisory

## Affected
- NuGet: `MongoDB.Driver` — affected >=0 <2.19.0

## Details
Under very specific circumstances, a privileged user is able to cause arbitrary code to be executed which may cause further disruption to services. This is specific to applications written in C#. This affects all MongoDB .NET/C# Driver versions prior to and including v2.18.0

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-48282
- https://github.com/mongodb/mongo-csharp-driver
- https://github.com/mongodb/mongo-csharp-driver/releases/tag/v2.19.0
- https://jira.mongodb.org/CSHARP-4475
- https://jira.mongodb.org/browse/CSHARP-4475
