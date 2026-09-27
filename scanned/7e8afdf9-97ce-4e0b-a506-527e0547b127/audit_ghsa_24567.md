# [M] Jenkins Klaros-Testmanagement Plugin stores credentials in plain text

## Summary
Severity: Medium
Advisory: GHSA-cr98-64h9-g8cg
CVE: CVE-2019-10282
CWE: CWE-522
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-cr98-64h9-g8cg
Type: github-advisory

## Affected
- Maven: `hudson.plugins.klaros:klaros-testmanagement` — affected >=0 <2.1.0

## Details
Jenkins Klaros-Testmanagement Plugin stores credentials unencrypted in job `config.xml` files on the Jenkins controller. These credentials can be viewed by users with Extended Read permission, or access to the Jenkins controller file system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10282
- https://github.com/jenkinsci/klaros-testmanagement-plugin/commit/7bab10557cc79918f8d61bb92652a7cafb154c22
- https://github.com/jenkinsci/klaros-testmanagement-plugin
- https://jenkins.io/security/advisory/2019-04-03/#SECURITY-843
- http://www.openwall.com/lists/oss-security/2019/04/12/2
