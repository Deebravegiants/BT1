# [M] Cross-site scripting (XSS) vulnerability in the user-profile biography section in DotNetNuke (DNN)

## Summary
Severity: Medium
Advisory: GHSA-5c66-x4wm-rjfx
CVE: CVE-2016-7119
CWE: CWE-79
Ecosystem: NuGet
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2018-10-16
Source: https://github.com/advisories/GHSA-5c66-x4wm-rjfx
Type: github-advisory

## Affected
- NuGet: `DotNetNuke.Core` — affected >=0 <8.0.1

## Details
Cross-site scripting (XSS) vulnerability in the user-profile biography section in DotNetNuke (DNN) before 8.0.1 allows remote authenticated users to inject arbitrary web script or HTML via a crafted onclick attribute in an IMG element.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-7119
- https://github.com/advisories/GHSA-5c66-x4wm-rjfx
- http://www.dnnsoftware.com/community/security/security-center
- http://www.securityfocus.com/bid/92719
