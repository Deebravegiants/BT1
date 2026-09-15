# [M] Jenkins Monitoring Plugin Reveals Sensitive Information via Unspecified Pages

## Summary
Severity: Medium
Advisory: GHSA-qwc3-p5pc-q93h
CVE: CVE-2014-3679
CWE: CWE-284
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-qwc3-p5pc-q93h
Type: github-advisory

## Affected
- Maven: `org.jvnet.hudson.plugins:monitoring` — affected >=0 <1.53.0

## Details
The Monitoring plugin before 1.53.0 for Jenkins allows remote attackers to obtain sensitive information by accessing unspecified pages.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-3679
- https://github.com/jenkinsci/monitoring-plugin/commit/f0f6aeef2032696c97d4b015dd51fa2b841b0473
- https://github.com/jenkinsci/monitoring-plugin
- https://wiki.jenkins-ci.org/display/JENKINS/Monitoring
- https://wiki.jenkins-ci.org/display/SECURITY/Jenkins+Security+Advisory+2014-10-01
