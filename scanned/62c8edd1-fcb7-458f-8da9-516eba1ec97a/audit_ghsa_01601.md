# [M] Heap buffer overflow in CefSharp

## Summary
Severity: Medium
Advisory: GHSA-pv36-h7jh-qm62
CVE: CVE-2020-15999
CWE: CWE-119, CWE-787
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2020-10-27
Source: https://github.com/advisories/GHSA-pv36-h7jh-qm62
Type: github-advisory

## Affected
- NuGet: `CefSharp.Common` — affected >=0 <85.3.130
- NuGet: `CefSharp.Wpf` — affected >=0 <85.3.130
- NuGet: `CefSharp.WinForms` — affected >=0 <85.3.130
- NuGet: `CefSharp.Wpf.HwndHost` — affected >=0 <85.3.130

## Details
### Impact
A memory corruption bug(Heap overflow) in the FreeType font rendering library.

> This can be exploited by attackers to execute arbitrary code by using specially crafted fonts with embedded PNG images .

As per https://www.secpod.com/blog/chrome-zero-day-under-active-exploitation-patch-now/ 

Google is aware of reports that an exploit for CVE-2020-15999 exists in the wild.

### Patches
Upgrade to 85.3.130 or higher

### References
- https://www.secpod.com/blog/chrome-zero-day-under-active-exploitation-patch-now/
- https://www.zdnet.com/article/google-releases-chrome-security-update-to-patch-actively-exploited-zero-day/
- https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2020-15999
- https://magpcss.org/ceforum/viewtopic.php?f=10&t=17942

To review the `CEF/Chromium` patch see https://bitbucket.org/chromiumembedded/cef/commits/cd6cbe008b127990036945fb75e7c2c1594ab10d

## References
- https://github.com/cefsharp/CefSharp/security/advisories/GHSA-pv36-h7jh-qm62
- https://nvd.nist.gov/vuln/detail/CVE-2020-15999
- https://www.nuget.org/packages/CefSharp.Wpf.HwndHost
- https://www.nuget.org/packages/CefSharp.Wpf
- https://www.nuget.org/packages/CefSharp.WinForms
- https://www.nuget.org/packages/CefSharp.Common
- https://www.debian.org/security/2021/dsa-4824
- https://security.netapp.com/advisory/ntap-20240812-0001
- https://security.gentoo.org/glsa/202401-19
- https://security.gentoo.org/glsa/202012-04
- https://security.gentoo.org/glsa/202011-12
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/J3QVIGAAJ4D62YEJAJJWMCCBCOQ6TVL7
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/J3QVIGAAJ4D62YEJAJJWMCCBCOQ6TVL7
- https://googleprojectzero.blogspot.com/p/rca-cve-2020-15999.html
- https://github.com/cefsharp/CefSharp
- https://crbug.com/1139963
- https://chromereleases.googleblog.com/2020/10/stable-channel-update-for-desktop_20.html
- http://lists.opensuse.org/opensuse-security-announce/2020-11/msg00016.html
- http://seclists.org/fulldisclosure/2020/Nov/33
