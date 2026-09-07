# [M] Incorrect Permission Assignment for Critical Resource in Jenkins Mailer Plugin

## Summary
Severity: Medium
Advisory: GHSA-558x-h7rg-997v
CVE: CVE-2022-20614
CWE: CWE-732, CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-01-13
Source: https://github.com/advisories/GHSA-558x-h7rg-997v
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:mailer` — affected >=391.ve4a38c1bcf4b <408.vd726a
- Maven: `org.jenkins-ci.plugins:mailer` — affected >=0 <1.34.2

## Details
Jenkins Mailer Plugin prior to 408.vd726a_1130320 and 1.34.2 does not perform a permission check in a method implementing form validation.

This allows attackers with Overall/Read access to use the DNS used by the Jenkins instance to resolve an attacker-specified hostname.

Additionally, this form validation method does not require POST requests, resulting in a cross-site request forgery (CSRF) vulnerability.

Mailer Plugin 408.vd726a_1130320 and 1.34.2 requires POST requests and Overall/Administer permission for the affected form validation method.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-20614
- https://github.com/jenkinsci/mailer-plugin/commit/5e6051fae61a43564e22aa89cb24ed8a42a26052
- https://www.jenkins.io/security/advisory/2022-01-12/#SECURITY-2163
- https://www.oracle.com/security-alerts/cpuapr2022.html
- http://www.openwall.com/lists/oss-security/2022/01/12/6
