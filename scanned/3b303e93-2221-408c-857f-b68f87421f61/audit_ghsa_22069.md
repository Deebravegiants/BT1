# [M] Improper authorization vulnerability in Jenkins Mesos Plugin

## Summary
Severity: Medium
Advisory: GHSA-23xr-9xxr-vg3c
CVE: CVE-2018-1000420
CWE: CWE-863
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-23xr-9xxr-vg3c
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:mesos` — affected >=0 <0.18

## Details
An improper authorization vulnerability exists in Jenkins Mesos Plugin 0.17.1 and earlier in MesosCloud.java that allows attackers with Overall/Read access to obtain credentials IDs for credentials stored in Jenkins.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000420
- https://jenkins.io/security/advisory/2018-09-25/#SECURITY-1013%20(1)
- http://www.securityfocus.com/bid/106532
