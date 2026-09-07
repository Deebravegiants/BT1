# [M] Stored XSS vulnerability in Jenkins Sonargraph Integration Plugin

## Summary
Severity: Medium
Advisory: GHSA-f799-hfg3-48jp
CVE: CVE-2020-2201
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-f799-hfg3-48jp
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:sonargraph-integration` — affected >=0 <3.0.1

## Details
Sonargraph Integration Plugin 3.0.0 and earlier does not escape the file path for the Log file field form validation.

This results in a stored cross-site scripting (XSS) vulnerability that can be exploited by users with Job/Configure permission.

Sonargraph Integration Plugin 3.0.1 escapes the affected part of the error message.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2201
- https://github.com/jenkinsci/sonargraph-integration-plugin
- https://jenkins.io/security/advisory/2020-07-02/#SECURITY-1775
- http://www.openwall.com/lists/oss-security/2020/07/02/7
