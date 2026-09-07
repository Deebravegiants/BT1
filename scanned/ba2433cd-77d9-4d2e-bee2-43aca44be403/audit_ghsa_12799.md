# [M] Apache Sling App CMS vulnerable to reflected Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-38m2-vr6g-8c94
CVE: CVE-2022-46769
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-01-09
Source: https://github.com/advisories/GHSA-38m2-vr6g-8c94
Type: github-advisory

## Affected
- Maven: `org.apache.sling:org.apache.sling.cms` — affected >=0 <1.1.4

## Details
An improper neutralization of input during web page generation ('Cross-site Scripting') [CWE-79] vulnerability in Sling App CMS version 1.1.2 and prior may allow an authenticated remote attacker to perform a reflected cross-site scripting (XSS) attack in the site group feature. Upgrade to Apache Sling App CMS >= 1.1.4

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-46769
- https://github.com/apache/sling-org-apache-sling-app-cms
- https://sling.apache.org/news.html
