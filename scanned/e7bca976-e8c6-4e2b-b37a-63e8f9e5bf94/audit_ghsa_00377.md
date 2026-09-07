# [H] ASP.NET Core fails to properly validate web requests

## Summary
Severity: High
Advisory: GHSA-6xh7-4v2w-36q6
CVE: CVE-2017-0247
CWE: CWE-20
Ecosystem: NuGet
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2018-10-16
Source: https://github.com/advisories/GHSA-6xh7-4v2w-36q6
Type: github-advisory

## Affected
- NuGet: `Microsoft.AspNetCore.Mvc` — affected >=1.0.0 <1.0.4
- NuGet: `Microsoft.AspNetCore.Mvc` — affected >=1.1.0 <1.1.3
- NuGet: `Microsoft.AspNetCore.Mvc.Core` — affected >=1.0.0 <1.0.4
- NuGet: `Microsoft.AspNetCore.Mvc.Core` — affected >=1.1.0 <1.1.3
- NuGet: `System.Net.Http` — affected >=4.1.1 <4.1.2
- NuGet: `System.Net.Http` — affected >=4.3.1 <4.3.2
- NuGet: `System.Text.Encodings.Web` — affected >=4.0.0 <4.0.1
- NuGet: `System.Text.Encodings.Web` — affected >=4.3.0 <4.3.1
- NuGet: `System.Net.Http.WinHttpHandler` — affected >=4.0.0 <4.0.1
- NuGet: `System.Net.Http.WinHttpHandler` — affected >=4.3.0 <4.5.4
- NuGet: `System.Net.Security` — affected >=4.0.0 <4.0.1
- NuGet: `System.Net.Security` — affected >=4.3.0 <4.3.1
- NuGet: `System.Net.WebSockets.Client` — affected >=4.0.0 <4.0.1
- NuGet: `System.Net.WebSockets.Client` — affected >=4.3.0 <4.3.1
- NuGet: `Microsoft.AspNetCore.Mvc.Abstractions` — affected >=1.0.0 <1.0.4
- NuGet: `Microsoft.AspNetCore.Mvc.Abstractions` — affected >=1.1.0 <1.1.3
- NuGet: `Microsoft.AspNetCore.Mvc.ApiExplorer` — affected >=1.0.0 <1.0.4
- NuGet: `Microsoft.AspNetCore.Mvc.ApiExplorer` — affected >=1.1.0 <1.1.3
- NuGet: `Microsoft.AspNetCore.Mvc.Cors` — affected >=1.0.0 <1.0.4
- NuGet: `Microsoft.AspNetCore.Mvc.Cors` — affected >=1.1.0 <1.1.3
- NuGet: `Microsoft.AspNetCore.Mvc.DataAnnotations` — affected >=1.0.0 <1.0.4
- NuGet: `Microsoft.AspNetCore.Mvc.DataAnnotations` — affected >=1.1.0 <1.1.3
- NuGet: `Microsoft.AspNetCore.Mvc.Formatters.Json` — affected >=1.0.0 <1.0.4
- NuGet: `Microsoft.AspNetCore.Mvc.Formatters.Json` — affected >=1.1.0 <1.1.3
- NuGet: `Microsoft.AspNetCore.Mvc.Formatters.Xml` — affected >=1.0.0 <1.0.4
- NuGet: `Microsoft.AspNetCore.Mvc.Formatters.Xml` — affected >=1.1.0 <1.1.3
- NuGet: `Microsoft.AspNetCore.Mvc.Localization` — affected >=1.0.0 <1.0.4
- NuGet: `Microsoft.AspNetCore.Mvc.Localization` — affected >=1.1.0 <1.1.3
- NuGet: `Microsoft.AspNetCore.Mvc.Razor.Host` — affected >=1.0.0 <1.0.4
- NuGet: `Microsoft.AspNetCore.Mvc.Razor.Host` — affected >=1.1.0 <1.1.3
- NuGet: `Microsoft.AspNetCore.Mvc.Razor` — affected >=1.0.0 <1.0.4
- NuGet: `Microsoft.AspNetCore.Mvc.Razor` — affected >=1.1.0 <1.1.3
- NuGet: `Microsoft.AspNetCore.Mvc.TagHelpers` — affected >=1.0.0 <1.0.4
- NuGet: `Microsoft.AspNetCore.Mvc.TagHelpers` — affected >=1.1.0 <1.1.3
- NuGet: `Microsoft.AspNetCore.Mvc.ViewFeatures` — affected >=1.0.0 <1.0.4
- NuGet: `Microsoft.AspNetCore.Mvc.ViewFeatures` — affected >=1.1.0 <1.1.3
- NuGet: `Microsoft.AspNetCore.Mvc.WebApiCompatShim` — affected >=1.0.0 <1.0.4
- NuGet: `Microsoft.AspNetCore.Mvc.WebApiCompatShim` — affected >=1.1.0 <1.1.3

## Details
A denial of service vulnerability exists when the ASP.NET Core fails to properly validate web requests. NOTE: Microsoft has not commented on third-party claims that the issue is that the TextEncoder.EncodeCore function in the System.Text.Encodings.Web package in ASP.NET Core Mvc before 1.0.4 and 1.1.x before 1.1.3 allows remote attackers to cause a denial of service by leveraging failure to properly calculate the length of 4-byte characters in the Unicode Non-Character range.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-0247
- https://github.com/aspnet/Announcements/issues/239
- https://github.com/advisories/GHSA-6xh7-4v2w-36q6
- https://technet.microsoft.com/en-us/library/security/4021279.aspx
- https://www.sidertia.com/Home/Community/Blog/2017/05/18/ASPNET-Core-Unicode-Non-Char-Encoding-DoS
