# [H] Use after free in CefSharp

## Summary
Severity: High
Advisory: GHSA-gvqv-779r-4jgp
CVE: CVE-2020-16017
CWE: CWE-416
Ecosystem: NuGet
Published: 2020-11-27
Source: https://github.com/advisories/GHSA-gvqv-779r-4jgp
Type: github-advisory

## Affected
- NuGet: `CefSharp.Common` — affected >=0 <86.0.241
- NuGet: `CefSharp.Wpf` — affected >=0 <86.0.241
- NuGet: `CefSharp.WinForms` — affected >=0 <86.0.241
- NuGet: `CefSharp.Wpf.HwndHost` — affected >=0 <86.0.241

## Details
CVE-2020-16017: Use after free in site isolation

- https://chromereleases.googleblog.com/2020/11/stable-channel-update-for-desktop_11.html
- https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2020-16017

Google is aware of reports that exploits for CVE-2020-16013 and CVE-2020-16017 exist in the wild.

There is currently little to no public information on the issue other than it has been flagged as `High` severity.

## References
- https://github.com/cefsharp/CefSharp/security/advisories/GHSA-gvqv-779r-4jgp
- https://nvd.nist.gov/vuln/detail/CVE-2020-16017
- https://chromereleases.googleblog.com/2020/11/stable-channel-update-for-desktop_11.html
- https://crbug.com/1146709
