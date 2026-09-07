# [M] Jenkins LDAP Plugin vulnerable to Cross-Site Request Forgery

## Summary
Severity: Medium
Advisory: GHSA-c9qp-6556-jwwp
CVE: CVE-2023-32978
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2023-05-16
Source: https://github.com/advisories/GHSA-c9qp-6556-jwwp
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:ldap` — affected >=0 <676.vfa

## Details
Jenkins LDAP Plugin 673.v034ec70ec2b_b_ and earlier does not require POST requests for a form validation method, resulting in a cross-site request forgery (CSRF) vulnerability.

This vulnerability allows attackers to connect to an attacker-specified LDAP server using attacker-specified credentials.

LDAP Plugin 676.vfa_64cf6b_b_002 requires POST requests for the affected form validation method.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-32978
- https://github.com/jenkinsci/ldap-plugin/commit/fa64cf6bb002f1b60a45fcd308d45b5a1047e687
- https://www.jenkins.io/security/advisory/2023-05-16/#SECURITY-3046
