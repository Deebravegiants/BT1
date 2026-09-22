# [M] Agent-to-controller security bypass in Jenkins Conjur Secrets Plugin allows decrypting secrets

## Summary
Severity: Medium
Advisory: GHSA-g7fx-mmjc-r7gv
CVE: CVE-2022-23116
CWE: CWE-311
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-01-13
Source: https://github.com/advisories/GHSA-g7fx-mmjc-r7gv
Type: github-advisory

## Affected
- Maven: `org.conjur.jenkins:conjur-credentials` — affected >=0 <1.0.10

## Details
Jenkins Conjur Secrets Plugin 1.0.9 and earlier implements functionality that allows attackers able to control agent processes to decrypt secrets stored in Jenkins obtained through another method.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-23116
- https://github.com/jenkinsci/conjur-credentials-plugin
- https://www.jenkins.io/security/advisory/2022-01-12/#SECURITY-2522%20(1)
- http://www.openwall.com/lists/oss-security/2022/01/12/6
