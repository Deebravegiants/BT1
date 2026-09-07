# [M] Cross-site Scripting in Jenkins Credentials Plugin

## Summary
Severity: Medium
Advisory: GHSA-rvg5-f5fj-mxvg
CVE: CVE-2022-29036
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-04-13
Source: https://github.com/advisories/GHSA-rvg5-f5fj-mxvg
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:credentials` — affected >=0 <2.6.1.1
- Maven: `org.jenkins-ci.plugins:credentials` — affected >=2.6.2 <1074.1076.v39c30cecb_0e2
- Maven: `org.jenkins-ci.plugins:credentials` — affected >=1087.v16065d268466 <1087.1089.v2f1b_9a_b_040e4
- Maven: `org.jenkins-ci.plugins:credentials` — affected >=1105

## Details
Jenkins Credentials Plugin 1111.v35a_307992395 and earlier, except 1087.1089.v2f1b_9a_b_040e4, 1074.1076.v39c30cecb_0e2, and 2.6.1.1, does not escape the name and description of Credentials parameters on views displaying parameters, resulting in a stored cross-site scripting (XSS) vulnerability exploitable by attackers with Item/Configure permission.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-29036
- https://www.jenkins.io/security/advisory/2022-04-12/#SECURITY-2617
