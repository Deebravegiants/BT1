# [M] Missing permission checks in Jenkins openstack-heat Plugin

## Summary
Severity: Medium
Advisory: GHSA-hm53-hrhh-gwfq
CVE: CVE-2022-36912
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-07-28
Source: https://github.com/advisories/GHSA-hm53-hrhh-gwfq
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:openstack-heat` — affected >=0

## Details
openstack-heat Plugin 1.5 and earlier does not perform permission checks in methods implementing form validation.

This allows attackers with Overall/Read permission to connect to an attacker-specified URL.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-36912
- https://github.com/jenkinsci/openstack-heat-plugin
- https://www.jenkins.io/security/advisory/2022-07-27/#SECURITY-2105%20(1)
- http://www.openwall.com/lists/oss-security/2022/07/27/1
