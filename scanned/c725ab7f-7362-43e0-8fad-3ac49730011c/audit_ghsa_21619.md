# [H] Use after free in Animation

## Summary
Severity: High
Advisory: GHSA-vv6j-ww6x-54gx
CVE: CVE-2022-0609
CWE: CWE-416
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-22
Source: https://github.com/advisories/GHSA-vv6j-ww6x-54gx
Type: github-advisory

## Affected
- NuGet: `CefSharp.Common` — affected >=0 <98.1.210
- NuGet: `CefSharp.OffScreen` — affected >=0 <98.1.210
- NuGet: `CefSharp.WinForms` — affected >=0 <98.1.210
- NuGet: `CefSharp.Wpf` — affected >=0 <98.1.210
- NuGet: `CefSharp.Wpf.HwndHost` — affected >=0 <98.1.210
- NuGet: `CefSharp.Common.NETCore` — affected >=0 <98.1.210
- NuGet: `CefSharp.OffScreen.NETCore` — affected >=0 <98.1.210
- NuGet: `CefSharp.WinForms.NETCore` — affected >=0 <98.1.210
- NuGet: `CefSharp.Wpf.NETCore` — affected >=0 <98.1.210

## Details
CVE-2022-0609: Use after free in Animation

- https://chromereleases.googleblog.com/2022/02/stable-channel-update-for-desktop_14.html
- https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2022-0609

Google is aware of reports that exploits for CVE-2022-0609 exist in the wild.

The exploitation is known to be easy. The attack may be initiated remotely. No form of authentication is needed for a successful exploitation. It demands that the victim is doing some kind of user interaction. Technical details are unknown but an exploit is available.

There is currently little other public information on the issue other than it has been flagged as `High` severity.

## References
- https://github.com/cefsharp/CefSharp/security/advisories/GHSA-vv6j-ww6x-54gx
- https://nvd.nist.gov/vuln/detail/CVE-2022-0609
- https://chromereleases.googleblog.com/2022/02/stable-channel-update-for-desktop_14.html
- https://crbug.com/1296150
- https://github.com/cefsharp/CefSharp
