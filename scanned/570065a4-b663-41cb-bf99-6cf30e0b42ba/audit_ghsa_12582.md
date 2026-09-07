# [M] Jenkins Digital.ai App Management Publisher Plugin missing permission checks

## Summary
Severity: Medium
Advisory: GHSA-5ghv-wxh9-7356
CVE: CVE-2023-35149
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2023-06-14
Source: https://github.com/advisories/GHSA-5ghv-wxh9-7356
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:ease-plugin` — affected >=0

## Details
Jenkins Digital.ai App Management Publisher Plugin 2.6 and earlier does not perform permission checks in several HTTP endpoints.

This allows attackers with Overall/Read permission to connect to an attacker-specified URL using attacker-specified credentials IDs obtained through another method, capturing credentials stored in Jenkins.

Additionally, these HTTP endpoints do not require POST requests, resulting in a cross-site request forgery (CSRF) vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-35149
- https://www.jenkins.io/security/advisory/2023-06-14/#SECURITY-2911
- http://www.openwall.com/lists/oss-security/2023/06/14/5
