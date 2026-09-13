# [M] Jenkins Zephyr Enterprise Test Management Plugin missing permission check

## Summary
Severity: Medium
Advisory: GHSA-4p5r-2m5c-hvcc
CVE: CVE-2019-1003085
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-4p5r-2m5c-hvcc
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:zephyr-enterprise-test-management` — affected >=0 <1.8

## Details
A missing permission check in Jenkins Zephyr Enterprise Test Management Plugin in the ZeeDescriptor#doTestConnection form validation method allows attackers with Overall/Read permission to initiate a connection to an attacker-specified server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-1003085
- https://github.com/jenkinsci/zephyr-enterprise-test-management-plugin/commit/a2a698660c12d78e06f78c813c3ff10b4c30db16
- https://github.com/jenkinsci/zephyr-enterprise-test-management-plugin
- https://jenkins.io/security/advisory/2019-04-03/#SECURITY-993
- http://www.openwall.com/lists/oss-security/2019/04/12/2
- http://www.securityfocus.com/bid/107790
