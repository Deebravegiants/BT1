# [M] Jenkins docker-build-step Plugin Cross-Site Request Forgery vulnerability

## Summary
Severity: Medium
Advisory: GHSA-64c5-r2h5-c2fg
CVE: CVE-2024-2215
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2024-03-06
Source: https://github.com/advisories/GHSA-64c5-r2h5-c2fg
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:docker-build-step` — affected >=0

## Details
A cross-site request forgery (CSRF) vulnerability in Jenkins docker-build-step Plugin 2.11 and earlier allows attackers to connect to an attacker-specified TCP or Unix socket URL, and to reconfigure the plugin using the provided connection test parameters, affecting future build step executions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-2215
- https://github.com/jenkinsci/docker-build-step-plugin
- https://www.jenkins.io/security/advisory/2024-03-06/#SECURITY-3200
- http://www.openwall.com/lists/oss-security/2024/03/06/3
