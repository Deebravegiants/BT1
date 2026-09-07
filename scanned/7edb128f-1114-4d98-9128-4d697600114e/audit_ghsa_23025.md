# [M] Improper Neutralization of Input During Web Page Generation Apache Sling Servlets Post

## Summary
Severity: Medium
Advisory: GHSA-8c82-9rgp-4qvr
CVE: CVE-2017-9802
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-8c82-9rgp-4qvr
Type: github-advisory

## Affected
- Maven: `org.apache.sling:org.apache.sling.servlets.post` — affected >=0 <2.3.22

## Details
The Javascript method Sling.evalString() in Apache Sling Servlets Post before 2.3.22 uses the javascript 'eval' function to parse input strings, which allows for XSS attacks by passing specially crafted input strings.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-9802
- https://issues.apache.org/jira/browse/SLING-7041
- https://lists.apache.org/thread.html/2f4b8333e44c6e7e0b00933bd4204ce64829952f60dbb6814f2cdf91@%3Cdev.sling.apache.org%3E
- http://packetstormsecurity.com/files/143758/Apache-Sling-Servlets-Post-2.3.20-Cross-Site-Scripting.html
- http://www.securityfocus.com/archive/1/541024/100/0/threaded
- http://www.securityfocus.com/bid/100284
