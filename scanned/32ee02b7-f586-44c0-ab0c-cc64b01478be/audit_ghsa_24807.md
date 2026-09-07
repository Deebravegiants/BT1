# [M] DotNetNuke Vulnerable to XSS in Pass-Through Values

## Summary
Severity: Medium
Advisory: GHSA-xr96-7ccp-pg5c
CVE: CVE-2007-0660
CWE: CWE-79
Ecosystem: NuGet
Published: 2022-05-01
Source: https://github.com/advisories/GHSA-xr96-7ccp-pg5c
Type: github-advisory

## Affected
- NuGet: `DotNetNuke.Core` — affected >=0 <03.02.01

## Details
Cross-site scripting (XSS) vulnerability in the IFrame module before 03.02.01 for DotNetNuke (DNN), caused by improper validation of user-supplied input by an unspecified script. Pass through values were not getting filtered, leaving them vulnerable to XSS.  A remote attacker could exploit this vulnerability using various parameters in a specially-crafted URL to execute script in a victim's Web browser within the security context of the hosting Web site, once the URL is clicked. An attacker could use this vulnerability to steal the victim's cookie-based authentication credentials.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2007-0660
- https://exchange.xforce.ibmcloud.com/vulnerabilities/32037
- https://web.archive.org/web/20071128032502/http://www.dotnetnuke.com/Default.aspx?tabid=825&EntryID=1278
- https://web.archive.org/web/20081007210427/http://www.securityfocus.com/bid/22334
