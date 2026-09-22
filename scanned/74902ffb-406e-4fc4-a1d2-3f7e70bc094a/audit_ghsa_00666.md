# [H] Inappropriate implementation in V8

## Summary
Severity: High
Advisory: GHSA-m7mf-48hp-5qmr
CVE: CVE-2020-16009
CWE: CWE-787
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2020-12-02
Source: https://github.com/advisories/GHSA-m7mf-48hp-5qmr
Type: github-advisory

## Affected
- NuGet: `CefSharp.Common` — affected >=0 <86.0.241
- NuGet: `CefSharp.Wpf` — affected >=0 <86.0.241
- NuGet: `CefSharp.WinForms` — affected >=0 <86.0.241
- NuGet: `CefSharp.Wpf.HwndHost` — affected >=0 <86.0.241

## Details
CVE-2020-16009: Inappropriate implementation in V8

- https://chromereleases.googleblog.com/2020/11/stable-channel-update-for-desktop.html
- https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2020-16009

Google is aware of reports that exploits for CVE-2020-16009 exist in the wild.

Allowed a remote attacker to potentially exploit heap corruption via a crafted HTML page.

There is currently little to no public information on the issue other than it has been flagged as `High` severity.

## References
- https://github.com/cefsharp/CefSharp/security/advisories/GHSA-m7mf-48hp-5qmr
- https://nvd.nist.gov/vuln/detail/CVE-2020-16009
- https://chromereleases.googleblog.com/2020/11/stable-channel-update-for-desktop.html
- https://crbug.com/1143772
- https://github.com/cefsharp/CefSharp
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/S4XYJ7B6OXHZNYSA5J3DBUOFEC6WCAGW
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/SC3U3H6AISVZB5PLZLLNF4HMQ4UFFL7M
- https://security.gentoo.org/glsa/202011-12
- https://www.debian.org/security/2021/dsa-4824
- http://lists.opensuse.org/opensuse-security-announce/2020-11/msg00016.html
- http://lists.opensuse.org/opensuse-security-announce/2020-11/msg00017.html
- http://packetstormsecurity.com/files/159974/Chrome-V8-Turbofan-Type-Confusion.html
