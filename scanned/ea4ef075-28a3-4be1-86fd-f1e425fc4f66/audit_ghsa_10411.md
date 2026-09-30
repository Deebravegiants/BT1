# [H] EnhancedLinq.Async is Vulnerable to Denial of Service via Transitive Dependency Microsoft.Bcl.Memory

## Summary
Severity: High
Advisory: GHSA-32wq-ppwg-3w4m
CWE: CWE-129, CWE-1395
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-04-01
Source: https://github.com/advisories/GHSA-32wq-ppwg-3w4m
Type: github-advisory

## Affected
- NuGet: `EnhancedLinq.Async` — affected >=1.0.0-beta.1 <1.0.0-beta.3

## Details
### Impact
`Microsoft.Bcl.Memory`, a transitive dependency of `EnhancedLinq.Async`, had a Denial of Service security vulnerability, [CVE-2026-26127](https://github.com/dotnet/announcements/issues/384), thus affecting `EnhancedLinq.Async` versions that had vulnerable versions of `Microsoft.Bcl.Memory` as a transitive dependency.

### Patches
`EnhancedLinq.Async` 1.0.0 Beta 3 updates the dependency on `System.Linq.AsyncEnumerable` to version 10.0.4 or newer which in turn updates the transitive dependency on `Microsoft.Bcl.Memory` from version 10.0.3 to 10.0.4 or newer, resolving the vulnerability.

### Workarounds
No workarounds exist for this vulnerability.

### How to fix the issue

To update the `EnhancedLinq.Async` NuGet package, use one of the following methods:

**NuGet Package Manager UI in Visual Studio:**
- Open the project in Visual Studio.
- Right-click on the project in Solution Explorer and select "Manage NuGet Packages..." or navigate to "Project > Manage NuGet Packages".
- In the NuGet Package Manager window, select the "Updates" tab. This tab lists packages with available updates from configured package sources.
- Select the package(s) to update. A specific version can be chosen from the dropdown, or the latest available version can be selected.
- Click the "Update" button.

**Using the NuGet Package Manager Console in Visual Studio:**
- Open the project in Visual Studio.
- Navigate to "Tools > NuGet Package Manager > Package Manager Console".
- To update a specific package to its latest version, use the following Update-Package command:

```
Update-Package -Id EnhancedLinq.Async
```

**Using the .NET CLI (Command Line Interface):**
- Open a terminal or command prompt in the project's directory.
- To update a specific package to its latest version, use the following add package command:

```
dotnet package update EnhancedLinq.Async
```

Once the NuGet package reference has been updated, the application must be recompiled and redeployed.

## References
- https://github.com/alastairlundy/EnhancedLinq/security/advisories/GHSA-32wq-ppwg-3w4m
- https://github.com/dotnet/announcements/issues/384
- https://github.com/alastairlundy/EnhancedLinq
- https://www.cve.org/CVERecord?id=CVE-2026-26127
