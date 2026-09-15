# [M] Jenkins DeployHub Plugin stores credentials in plain text

## Summary
Severity: Medium
Advisory: GHSA-9m3c-xfhf-53mh
CVE: CVE-2019-10286
CWE: CWE-522
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-9m3c-xfhf-53mh
Type: github-advisory

## Affected
- Maven: `com.openmake:deployhub` — affected >=0 <8.0.14

## Details
Jenkins DeployHub Plugin stores credentials unencrypted in job `config.xml` files on the Jenkins controller. These credentials can be viewed by users with Extended Read permission, or access to the Jenkins controller file system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10286
- https://github.com/jenkinsci/deployhub-plugin/commit/6ad56362087f6d34c3532a0962a881cd8a822394
- https://github.com/jenkinsci/deployhub-plugin
- https://jenkins.io/security/advisory/2019-04-03/#SECURITY-959
- http://www.openwall.com/lists/oss-security/2019/04/12/2
