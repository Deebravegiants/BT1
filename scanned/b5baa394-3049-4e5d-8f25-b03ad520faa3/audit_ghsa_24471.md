# [M] Jenkins Sonar Gerrit Plugin stores credentials unencrypted

## Summary
Severity: Medium
Advisory: GHSA-6fv3-w7j6-5xfc
CVE: CVE-2019-10467
CWE: CWE-522
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-6fv3-w7j6-5xfc
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:sonar-gerrit` — affected >=0 <2.4.5

## Details
Jenkins Sonar Gerrit Plugin stores credentials unencrypted in job config.xml files on the Jenkins master where they can be viewed by users with Extended Read permission, or access to the master file system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10467
- https://github.com/jenkinsci/sonar-gerrit-plugin/commit/d86de84131660051de7a90195478761b7d087630
- https://github.com/jenkinsci/sonar-gerrit-plugin
- https://jenkins.io/security/advisory/2019-10-23/#SECURITY-1003
- http://www.openwall.com/lists/oss-security/2019/10/23/2
