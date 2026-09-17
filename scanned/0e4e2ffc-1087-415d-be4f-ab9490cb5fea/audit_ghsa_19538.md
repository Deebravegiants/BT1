# [H] CefSharp affected by incorrect handle provided in unspecified circumstances in Mojo on Windows

## Summary
Severity: High
Advisory: GHSA-f87w-3j5w-v58p
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2025-04-12
Source: https://github.com/advisories/GHSA-f87w-3j5w-v58p
Type: github-advisory

## Affected
- NuGet: `CefSharp.Wpf` — affected >=0 <134.3.90
- NuGet: `CefSharp.Wpf.HwndHost` — affected >=0 <134.3.90
- NuGet: `CefSharp.Wpf.NetCore` — affected >=0 <134.3.90
- NuGet: `CefSharp.WinForms` — affected >=0 <134.3.90
- NuGet: `CefSharp.WinForms.NetCore` — affected >=0 <134.3.90
- NuGet: `CefSharp.OffScreen.NetCore` — affected >=0 <134.3.90
- NuGet: `CefSharp.OffScreen` — affected >=0 <134.3.90

## Details
Incorrect handle provided in unspecified circumstances in Mojo in Google Chrome on Windows prior to 134.0.6998.177 allowed a remote attacker to perform a sandbox escape via a malicious file. (Chromium security severity: High)

https://nvd.nist.gov/vuln/detail/CVE-2025-2783
https://chromereleases.googleblog.com/2025/03/stable-channel-update-for-desktop_25.html
https://issues.chromium.org/issues/405143032

## References
- https://github.com/cefsharp/CefSharp/security/advisories/GHSA-f87w-3j5w-v58p
- https://nvd.nist.gov/vuln/detail/CVE-2025-2783
- https://chromereleases.googleblog.com/2025/03/stable-channel-update-for-desktop_25.html
- https://github.com/cefsharp/CefSharp
- https://github.com/cefsharp/CefSharp/releases/tag/v134.3.90
- https://issues.chromium.org/issues/405143032
