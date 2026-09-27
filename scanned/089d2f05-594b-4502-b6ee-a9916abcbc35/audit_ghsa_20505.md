# [M] Access key stored in plain text by Jenkins Metrics Plugin

## Summary
Severity: Medium
Advisory: GHSA-gg9m-x3cg-69vh
CVE: CVE-2022-20621
CWE: CWE-522
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-01-13
Source: https://github.com/advisories/GHSA-gg9m-x3cg-69vh
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:metrics` — affected >=4.0.2.8 <4.0.2.8.1
- Maven: `org.jenkins-ci.plugins:metrics` — affected >=0 <4.0.2.7.1

## Details
Jenkins Metrics Plugin 4.0.2.8 and earlier stores an access key unencrypted in its global configuration file `jenkins.metrics.api.MetricsAccessKey.xml` on the Jenkins controller as part of its configuration.

This access key can be viewed by users with access to the Jenkins controller file system.

Jenkins Metrics Plugin 4.0.2.8.1 stores access key encrypted once its configuration is saved again.

Additionally, the token value is only displayed once when it is generated.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-20621
- https://github.com/jenkinsci/metrics-plugin/commit/9810480370d4c5e04a2b710934db5461bde0d1b6
- https://github.com/jenkinsci/metrics-plugin
- https://www.jenkins.io/security/advisory/2022-01-12/#SECURITY-1624
- http://www.openwall.com/lists/oss-security/2022/01/12/6
