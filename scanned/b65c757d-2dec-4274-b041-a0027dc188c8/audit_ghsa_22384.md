# [M] Jenkins Agiletestware Pangolin Connector for TestRail Plugin CSRF vulnerability and missing permission checks

## Summary
Severity: Medium
Advisory: GHSA-pwrm-8mvm-p2f2
CVE: CVE-2018-1999032
CWE: CWE-269
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-pwrm-8mvm-p2f2
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:pangolin-testrail-connector` — affected >=0 <2.2

## Details
A data modification vulnerability exists in Jenkins Agiletestware Pangolin Connector for TestRail Plugin 2.1 and earlier in GlobalConfig.java that allows attackers with Overall/Read permission to override this plugin's configuration by sending crafted HTTP requests to an unprotected endpoint.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1999032
- https://github.com/jenkinsci/pangolin-testrail-connector-plugin/commit/53dac4413cca6947566589c0d0f85dee0100ffd5
- https://github.com/jenkinsci/pangolin-testrail-connector-plugin
- https://jenkins.io/security/advisory/2018-07-30/#SECURITY-995
