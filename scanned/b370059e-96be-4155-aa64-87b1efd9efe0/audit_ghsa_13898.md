# [H] Cross-Site Request Forgery in Jenkins Azure Credentials Plugin

## Summary
Severity: High
Advisory: GHSA-rr93-7c6x-8v4v
CVE: CVE-2023-25767
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-02-15
Source: https://github.com/advisories/GHSA-rr93-7c6x-8v4v
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:azure-credentials` — affected >=0 <254.v64da_8176c83a

## Details
A cross-site request forgery (CSRF) vulnerability in Jenkins Azure Credentials Plugin 253.v887e0f9e898b and earlier allows attackers to connect to an attacker-specified web server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-25767
- https://github.com/jenkinsci/azure-credentials-plugin/commit/64da8176c83a41bb83d3ad759628c9bd275b42f5
- https://github.com/jenkinsci/azure-credentials-plugin
- https://www.jenkins.io/security/advisory/2023-02-15/#SECURITY-1756
- http://www.openwall.com/lists/oss-security/2023/02/15/4
