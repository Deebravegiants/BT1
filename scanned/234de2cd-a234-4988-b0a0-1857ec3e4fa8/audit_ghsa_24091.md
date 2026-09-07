# [M] DotNetNuke Default Machine Key Exposure

## Summary
Severity: Medium
Advisory: GHSA-grw3-hjjm-5cjm
CVE: CVE-2008-6540
CWE: CWE-453
Ecosystem: NuGet
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-grw3-hjjm-5cjm
Type: github-advisory

## Affected
- NuGet: `DotNetNuke.Core` — affected >=0 <4.8.2

## Details
DotNetNuke before 4.8.2, during installation or upgrade, does not warn the administrator when the default (1) ValidationKey and (2) DecryptionKey values cannot be modified in the web.config file, which allows remote attackers to bypass intended access restrictions by using the default keys.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2008-6540
- https://exchange.xforce.ibmcloud.com/vulnerabilities/41399
- https://github.com/dnnsoftware/Dnn.Platform
- http://osvdb.org/43720
- http://secunia.com/advisories/29488
- http://www.dotnetnuke.com/News/SecurityBulletins/SecurityBulletinno12/tabid/1148/Default.aspx
- http://www.securityfocus.com/archive/1/489957/100/0/threaded
- http://www.securityfocus.com/bid/28391
