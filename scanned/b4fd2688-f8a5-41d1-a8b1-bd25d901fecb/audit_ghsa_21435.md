# [M] Jenkins Reverse Proxy Auth Plugin vulnerable due to plaintext storage of passwords

## Summary
Severity: Medium
Advisory: GHSA-wcjj-qm5v-j4pc
CVE: CVE-2022-45384
CWE: CWE-256, CWE-522
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-11-16
Source: https://github.com/advisories/GHSA-wcjj-qm5v-j4pc
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:reverse-proxy-auth-plugin` — affected >=1.7.3 <1.7.4

## Details
Jenkins Reverse Proxy Auth Plugin versions 1.7.3 and earlier stores the LDAP manager password unencrypted in the global config.xml file on the Jenkins controller where it can be viewed by attackers with access to the Jenkins controller file system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-45384
- https://github.com/jenkinsci/reverse-proxy-auth-plugin
- https://www.jenkins.io/security/advisory/2022-11-15/#SECURITY-2094
- http://www.openwall.com/lists/oss-security/2022/11/15/4
