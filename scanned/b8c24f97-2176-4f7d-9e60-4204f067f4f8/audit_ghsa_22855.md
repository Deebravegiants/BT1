# [M] Jenkins WebSphere Deployer Plugin stores credentials in plain text

## Summary
Severity: Medium
Advisory: GHSA-rqf2-4ggc-c74w
CVE: CVE-2019-1003056
CWE: CWE-311
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-rqf2-4ggc-c74w
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:websphere-deployer` — affected >=0

## Details
Jenkins WebSphere Deployer Plugin stores credentials unencrypted in job `config.xml` files on the Jenkins controller. These credentials can be viewed by users with Extended Read permission, or access to the Jenkins controller file system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-1003056
- https://jenkins.io/security/advisory/2019-04-03/#SECURITY-956
- http://www.openwall.com/lists/oss-security/2019/04/12/2
