# [M] Jenkins ElasticBox CI Plugin missing permission check

## Summary
Severity: Medium
Advisory: GHSA-gg44-xm5p-x9cm
CVE: CVE-2023-37965
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2023-07-12
Source: https://github.com/advisories/GHSA-gg44-xm5p-x9cm
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:elasticbox` — affected >=0

## Details
Jenkins ElasticBox CI Plugin 5.0.1 and earlier does not perform permission checks in several HTTP endpoints.

This allows attackers with Overall/Read permission to connect to an attacker-specified URL using attacker-specified credentials IDs obtained through another method, capturing credentials stored in Jenkins.

Additionally, these HTTP endpoints do not require POST requests, resulting in a cross-site request forgery (CSRF) vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-37965
- https://www.jenkins.io/security/advisory/2023-07-12/#SECURITY-3131
- http://www.openwall.com/lists/oss-security/2023/07/12/2
