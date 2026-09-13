# [M] Jenkins Configuration as Code Plugin vulnerable to Exposure of Sensitive Information

## Summary
Severity: Medium
Advisory: GHSA-393r-r9mq-g9jv
CVE: CVE-2018-1000609
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-393r-r9mq-g9jv
Type: github-advisory

## Affected
- Maven: `io.jenkins:configuration-as-code` — affected >=0 <0.8-alpha

## Details
A exposure of sensitive information vulnerability exists in Jenkins Configuration as Code Plugin 0.7-alpha and earlier in ConfigurationAsCode.java that allows attackers with Overall/Read access to obtain the YAML export of the Jenkins configuration. Version 0.8-alpha contains a fix for this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000609
- https://jenkins.io/security/advisory/2018-06-25/#SECURITY-927
