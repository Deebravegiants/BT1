# [M] DotNetNuke (DNN) Cross-site scripting (XSS) vulnerability via the __dnnVariable parameter

## Summary
Severity: Medium
Advisory: GHSA-rvrj-j7cc-236p
CVE: CVE-2013-4649
CWE: CWE-79
Ecosystem: NuGet
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-rvrj-j7cc-236p
Type: github-advisory

## Affected
- NuGet: `DotNetNuke.Core` — affected >=0 <6.2.9
- NuGet: `DotNetNuke.Core` — affected >=7.0 <7.1.1

## Details
Cross-site scripting (XSS) vulnerability in DotNetNuke (DNN) before 6.2.9 and 7.x before 7.1.1 allows remote attackers to inject arbitrary web script or HTML via the __dnnVariable parameter to the default URI.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-4649
- https://exchange.xforce.ibmcloud.com/vulnerabilities/86432
- https://github.com/dnnsoftware/Dnn.Platform
- http://packetstormsecurity.com/files/122792/DotNetNuke-DNN-7.1.0-6.2.8-Cross-Site-Scripting.html
- http://secunia.com/advisories/53493
- http://www.dnnsoftware.com/platform/manage/security-center
