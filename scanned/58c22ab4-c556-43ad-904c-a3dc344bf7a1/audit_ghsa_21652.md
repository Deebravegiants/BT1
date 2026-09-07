# [M] Jenkins Snow Commander Plugin 2.0 vulnerable to Cross-Site Request Forgery

## Summary
Severity: Medium
Advisory: GHSA-fhfh-6cjg-57rg
CVE: CVE-2022-25192
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-02-16
Source: https://github.com/advisories/GHSA-fhfh-6cjg-57rg
Type: github-advisory

## Affected
- Maven: `io.jenkins.plugins:embotics-vcommander` — affected >=0

## Details
A cross-site request forgery (CSRF) vulnerability in Jenkins Snow Commander Plugin 2.0 and earlier allows attackers to connect to an attacker-specified webserver using attacker-specified credentials IDs obtained through another method, capturing credentials stored in Jenkins.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25192
- https://github.com/jenkinsci/snowsoftware-commander-plugin/commit/4fb4e68e8e7be3168721a06ad08b263252c276f1
- https://github.com/jenkinsci/snowsoftware-commander-plugin
- https://www.jenkins.io/security/advisory/2022-02-15/#SECURITY-2536
