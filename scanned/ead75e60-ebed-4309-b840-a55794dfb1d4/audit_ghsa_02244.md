# [M] ASP.NET Core Information Disclosure Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-q7cg-43mg-qp69
CVE: CVE-2021-34532
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-q7cg-43mg-qp69
Type: github-advisory

## Affected
- NuGet: `Microsoft.AspNetCore.Authentication.JwtBearer` — affected >=2.1.0 <2.1.29
- NuGet: `Microsoft.AspNetCore.Authentication.JwtBearer` — affected >=3.0.0 <3.1.18
- NuGet: `Microsoft.AspNetCore.Authentication.JwtBearer` — affected >=5.0.0 <5.0.9

## Details
Microsoft is releasing this security advisory to provide information about a vulnerability in .NET 5.0, .NET Core 3.1 and .NET Core 2.1. This advisory also provides guidance on what developers can do to update their applications to remove this vulnerability.

An information disclosure vulnerability exists in .NET 5.0, .NET Core 3.1 and .NET Core 2.1 where a JWT token is logged if it cannot be parsed.

### Patches

* If you're using .NET 5.0, you should download and install Runtime 5.0.9 or SDK 5.0.206 (for Visual Studio 2019 v16.8) or SDK 5.0.303 (for Visual Studio 2019 V16.10) from https://dotnet.microsoft.com/download/dotnet-core/5.0.

* If you're using .NET Core 3.1, you should download and install Runtime 3.1.18 or SDK 3.1.118 (for Visual Studio 2019 v16.4) or 3.1.412 (for Visual Studio 2019 v16.7 or later) from https://dotnet.microsoft.com/download/dotnet-core/3.1.

* If you're using .NET Core 2.1, you should download and install Runtime 2.1.29 or SDK 2.1.525 (for Visual Studio 2019 v15.9) or 2.1.817 from https://dotnet.microsoft.com/download/dotnet-core/2.1.

* If your application is using .NET Core 2.1 running on .NET Framework see the [Updating .NET Core 2.1 on .NET Framework](#updating-2.1) section below.

### <a name="updating-2.1"></a> Updating .NET Core 2.1 on .NET Framework
If you are running .NET Core 2.1 on .NET Framework you need to check your projects for dependencies and update them accordingly.

#### Direct dependencies

Direct dependencies are discoverable by examining your `csproj` file. They can be fixed by [editing the project file](#fixing-direct-dependencies) or using NuGet to update the dependency.

#### Transitive dependencies

Transitive dependencies occur when you add a package to your project that in turn relies on another package. For example, if Contoso publishes a package `Contoso.Utility` which, in turn, depends on `Contoso.Internals` and you add the `Contoso.Utility` package to your project now your project has a direct dependency on `Contoso.Utility` and, because `Contoso.Utility` depends 'Contoso.Internals', your application gains a transitive dependency on the `Contoso.Internals` package.

Transitive dependencies are reviewable in two ways:

* In the Visual Studio Solution Explorer window, which supports searching.
* By examining the `project.assets.json` file contained in the obj directory of your project for `csproj` based projects

The `project.assets.json` files are the authoritative list of all packages used by your project, containing both direct and transitive dependencies.

There are two ways to view transitive dependencies. You can either [use Visual Studio’s Solution Explorer](#vs-solution-explorer), or you can review [the `project.assets.json` file](#project-assets-json)).

##### <a name="vs-solution-explorer"></a>Using Visual Studio Solution Explorer

To use Solution Explorer, open the project in Visual Studio, and then press Ctrl+; to activate the search in Solution Explorer. Search for the [vulnerable package](#affected-software) and make a note of the version numbers of any results you find.

For example, search for `Microsoft.AspNetCore.Authentication.JwtBearer` and update the package to the latest version


##### <a name="project-assets-json"></a> Manually reviewing project.assets.json

Open the *project.assets.json* file from your project’s obj directory in your editor. We suggest you use an editor that understands JSON and allows you to collapse and expand nodes to review this file.
Visual Studio and Visual Studio Code provide JSON friendly editing.

Search the *project.assets.json* file for the [vulnerable package](#affected-software), using the format `packagename/` for each of the package names from the preceding table. If you find the assembly name in your search:

* Examine the line on which they are found, the version number is after the `/`.
* Compare to the [vulnerable versions table](#affected-software).

For example, a search result that shows `Microsoft.AspNetCore.Authentication.JwtBearer/2.1.0` is a reference to version 2.1.1 of `Microsoft.AspNetCore.Authentication.JwtBearer`.

If your *project.assets.json* file includes references to the [vulnerable package](#affected-software), then you need to fix the transitive dependencies.

If you have not found any reference to any vulnerable packages, this means either

* None of your direct dependencies depend on any vulnerable packages, or
* You have already fixed the problem by updating the direct dependencies.

#### Other Details

- Announcement for this issue can be found at https://github.com/dotnet/announcements/issues/195
- An Issue for this can be found at https://github.com/dotnet/aspnetcore/issues/35246
- MSRC details for this can be found at https://msrc.microsoft.com/update-guide/en-US/vulnerability/CVE-2021-34532

## References
- https://github.com/dotnet/aspnetcore/security/advisories/GHSA-q7cg-43mg-qp69
- https://nvd.nist.gov/vuln/detail/CVE-2021-34532
- https://github.com/dotnet/aspnetcore
- https://msrc.microsoft.com/update-guide/vulnerability/CVE-2021-34532
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2021-34532
