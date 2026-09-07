# [M] Mono ASP.NET View State Cross-Site Scripting (XSS) vulnerability

## Summary
Severity: Medium
Advisory: GHSA-g5c6-w479-93xm
CVE: CVE-2010-1459
CWE: CWE-79
Ecosystem: NuGet
Published: 2022-05-02
Source: https://github.com/advisories/GHSA-g5c6-w479-93xm
Type: github-advisory

## Affected
- NuGet: `mono` — affected >=0 <2.6.4

## Details
The default configuration of ASP.NET in Mono before 2.6.4 has a value of FALSE for the EnableViewStateMac property, which allows remote attackers to conduct cross-site scripting (XSS) attacks, as demonstrated by the __VIEWSTATE parameter to 2.0/menu/menu1.aspx in the XSP sample project.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2010-1459
- https://github.com/mono/mono
- http://lists.opensuse.org/opensuse-security-announce/2010-05/msg00002.html
- http://lists.opensuse.org/opensuse-security-announce/2010-06/msg00001.html
- http://lists.opensuse.org/opensuse-security-announce/2010-08/msg00001.html
- http://www.communities.hp.com/securitysoftware/blogs/spilabs/archive/2010/04/29/asp-net-cross-site-scripting-followup-mono.aspx
- http://www.mono-project.com/Vulnerabilities#ASP.NET_View_State_Cross-Site_Scripting
- http://www.securityfocus.com/bid/40351
