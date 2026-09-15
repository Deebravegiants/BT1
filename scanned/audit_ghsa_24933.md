# [M] Jenkins Trac Publisher Plugin stores credentials in plain text

## Summary
Severity: Medium
Advisory: GHSA-577w-62cp-f67h
CVE: CVE-2019-1003067
CWE: CWE-311
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-577w-62cp-f67h
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:trac-publisher-plugin` — affected >=0

## Details
Jenkins Trac Publisher Plugin stores credentials unencrypted in job `config.xml` files on the Jenkins controller. These credentials can be viewed by users with Extended Read permission, or access to the Jenkins controller file system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-1003067
- https://jenkins.io/security/advisory/2019-04-03/#SECURITY-842
- http://www.openwall.com/lists/oss-security/2019/04/12/2
