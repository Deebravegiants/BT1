# [M] Jenkins Cadence vManager Plugin Vulnerable to Cross-Site Request Forgery

## Summary
Severity: Medium
Advisory: GHSA-5w52-96jj-fv59
CVE: CVE-2025-47886
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2025-05-14
Source: https://github.com/advisories/GHSA-5w52-96jj-fv59
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:vmanager-plugin` — affected >=0 <4.0.1-288.v8804b_ea_a_cb_7f

## Details
A cross-site request forgery (CSRF) vulnerability in Jenkins Cadence vManager Plugin 4.0.1-286.v9e25a_740b_a_48 and earlier allows attackers to connect to an attacker-specified URL using attacker-specified username and password.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-47886
- https://github.com/jenkinsci/vmanager-plugin/pull/25
- https://github.com/jenkinsci/vmanager-plugin
- https://github.com/jenkinsci/vmanager-plugin/releases/tag/4.0.1-288.v8804b_ea_a_cb_7f
- https://www.jenkins.io/security/advisory/2025-05-14/#SECURITY-3548
