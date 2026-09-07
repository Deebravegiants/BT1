# [M] Jenkins NeuVector Vulnerability Scanner Plugin Cross-Site Request Forgery vulnerability

## Summary
Severity: Medium
Advisory: GHSA-wpfc-r5qq-7r7p
CVE: CVE-2023-49673
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2023-11-29
Source: https://github.com/advisories/GHSA-wpfc-r5qq-7r7p
Type: github-advisory

## Affected
- Maven: `io.jenkins.plugins:neuvector-vulnerability-scanner` — affected >=0 <2.2

## Details
Jenkins NeuVector Vulnerability Scanner Plugin 1.22 and earlier does not perform a permission check in a connection test HTTP endpoint. This allows attackers with Overall/Read permission to connect to an attacker-specified hostname and port using attacker-specified username and password. Additionally, this HTTP endpoint does not require POST requests, resulting in a cross-site request forgery (CSRF) vulnerability.

NeuVector Vulnerability Scanner Plugin 2.2 requires POST requests and Overall/Administer permission for the affected HTTP endpoint.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-49673
- https://github.com/jenkinsci/neuvector-vulnerability-scanner-plugin
- https://www.jenkins.io/security/advisory/2023-11-29/#SECURITY-3256
- http://www.openwall.com/lists/oss-security/2023/11/29/1
