# [M] Jenkins ElectricFlow Plugin globally and unconditionally disabled SSL/TLS certificate validation

## Summary
Severity: Medium
Advisory: GHSA-xmqv-pfw7-qmj7
CVE: CVE-2019-10334
CWE: CWE-295
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-xmqv-pfw7-qmj7
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:electricflow` — affected >=0 <1.1.7

## Details
CloudBees CD Plugin unconditionally disabled SSL/TLS certificate validation for the entire Jenkins controller JVM during the deployment/publication of an application.

CloudBees CD Plugin no longer does that. Instead, the existing opt-in option to ignore SSL/TLS errors is used during deployment for the specific connection.

This issue was caused by an incomplete fix for [SECURITY-937](https://www.jenkins.io/security/advisory/2019-02-19/#SECURITY-937).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10334
- https://github.com/jenkinsci/electricflow-plugin/commit/d0b807d5e2de07a90d902401bae033c2907b850a
- https://jenkins.io/security/advisory/2019-06-11/#SECURITY-1411
- https://web.archive.org/web/20200227033720/http://www.securityfocus.com/bid/108747
- http://www.openwall.com/lists/oss-security/2019/06/11/1
