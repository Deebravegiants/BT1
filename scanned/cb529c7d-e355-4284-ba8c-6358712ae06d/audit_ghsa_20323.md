# [M] Plaintext Storage of a Password in Jenkins Convertigo Mobile Platform Plugin 

## Summary
Severity: Medium
Advisory: GHSA-c8mf-mc3f-2wvc
CVE: CVE-2022-34199
CWE: CWE-256, CWE-522
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-06-24
Source: https://github.com/advisories/GHSA-c8mf-mc3f-2wvc
Type: github-advisory

## Affected
- Maven: `com.convertigo.jenkins.plugins:convertigo-mobile-platform` — affected >=0

## Details
Jenkins Convertigo Mobile Platform Plugin 1.1 and earlier stores passwords unencrypted in job `config.xml` files on the Jenkins controller where they can be viewed by users with Extended Read permission, or access to the Jenkins controller file system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-34199
- https://github.com/jenkinsci/convertigo-mobile-platform-plugin
- https://www.jenkins.io/security/advisory/2022-06-22/#SECURITY-2064
