# [M] XSS in MITREid Connect

## Summary
Severity: Medium
Advisory: GHSA-c2h6-7gm8-cv4w
CVE: CVE-2020-5497
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2020-04-01
Source: https://github.com/advisories/GHSA-c2h6-7gm8-cv4w
Type: github-advisory

## Affected
- Maven: `org.mitre:openid-connect-server` — affected >=0

## Details
The OpenID Connect reference implementation for MITREid Connect through 1.3.3 allows XSS due to userInfoJson being included in the page unsanitized. This is related to header.tag. The issue can be exploited to execute arbitrary JavaScript.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-5497
- https://github.com/mitreid-connect/OpenID-Connect-Java-Spring-Server/issues/1521
- https://github.com/mitreid-connect/OpenID-Connect-Java-Spring-Server/pull/1526
- https://github.com/mitreid-connect/OpenID-Connect-Java-Spring-Server/pull/1527
- https://www.securitymetrics.com/blog/MITREid-Connect-cross-site-scripting-CVE-2020-5497
- http://packetstormsecurity.com/files/156574/MITREid-1.3.3-Cross-Site-Scripting.html
- http://seclists.org/fulldisclosure/2020/Feb/25
