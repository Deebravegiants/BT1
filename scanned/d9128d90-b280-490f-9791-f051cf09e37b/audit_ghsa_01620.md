# [H] Inappropriate implementation in V8 in CefSharp

## Summary
Severity: High
Advisory: GHSA-x7fx-mcc9-27j7
CVE: CVE-2020-16013
CWE: CWE-119, CWE-787
Ecosystem: NuGet
Published: 2020-11-27
Source: https://github.com/advisories/GHSA-x7fx-mcc9-27j7
Type: github-advisory

## Affected
- NuGet: `CefSharp.Common` — affected >=0 <86.0.241
- NuGet: `CefSharp.Wpf` — affected >=0 <86.0.241
- NuGet: `CefSharp.WinForms` — affected >=0 <86.0.241
- NuGet: `CefSharp.Wpf.HwndHost` — affected >=0 <86.0.241

## Details
High CVE-2020-16013: Inappropriate implementation in V8. 

- https://chromereleases.googleblog.com/2020/11/stable-channel-update-for-desktop_11.html
- https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2020-16013

Google is aware of reports that exploits for CVE-2020-16013 and CVE-2020-16017 exist in the wild.

There is currently little to no public information on the issue other than it has been flagged as `High` severity.

## References
- https://github.com/cefsharp/CefSharp/security/advisories/GHSA-x7fx-mcc9-27j7
- https://nvd.nist.gov/vuln/detail/CVE-2020-16013
- https://chromereleases.googleblog.com/2020/11/stable-channel-update-for-desktop_11.html
- https://crbug.com/1147206
