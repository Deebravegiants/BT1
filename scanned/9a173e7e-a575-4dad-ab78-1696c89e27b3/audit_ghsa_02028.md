# [M] Cross-site Scripting in Jenkins Dashboard View Plugin

## Summary
Severity: Medium
Advisory: GHSA-jwhm-9cjm-4493
CVE: CVE-2021-21649
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-06-16
Source: https://github.com/advisories/GHSA-jwhm-9cjm-4493
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:dashboard-view` — affected >=2.13 <2.16
- Maven: `org.jenkins-ci.plugins:dashboard-view` — affected >=0 <2.12.1

## Details
Jenkins Dashboard View Plugin prior to 2.16 and 2.12.1 does not escape URLs referenced in Image Dashboard Portlets, resulting in a stored cross-site scripting (XSS) vulnerability exploitable by attackers with View/Configure permission.

As part of this fix, the property for image URLs was changed from `url` to `imageUrl`. Existing [Configuration as Code](https://plugins.jenkins.io/configuration-as-code/) configurations are still supported, but exports will emit the new property.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-21649
- https://github.com/jenkinsci/dashboard-view-plugin/commit/586817b081d903e47cfdd05b96b8aae1d2c2700b
- https://github.com/CVEProject/cvelist/blob/2d78eb36f4d084db7fb35f1535d8d84fdcb7d859/2021/21xxx/CVE-2021-21649.json
- https://github.com/jenkinsci/dashboard-view-plugin
- https://www.jenkins.io/security/advisory/2021-05-11/#SECURITY-2233
