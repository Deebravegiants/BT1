# [M] Jenkins Team Concert Plugin does not perform permission checks in methods implementing form validation

## Summary
Severity: Medium
Advisory: GHSA-hcpw-v727-64qh
CVE: CVE-2023-3315
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-06-19
Source: https://github.com/advisories/GHSA-hcpw-v727-64qh
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:teamconcert` — affected >=0 <2.4.2

## Details
Jenkins Team Concert Plugin 2.4.1 and earlier does not perform permission checks in methods implementing form validation.

This allows attackers with Overall/Read permission to check for the existence of an attacker-specified file path on the Jenkins controller file system.

Team Concert Plugin 2.4.2 requires Overall/Administer permission for the affected form validation methods.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-3315
- https://github.com/jenkinsci/teamconcert-plugin/commit/c77dc8406070edead2a697f26f629465fef72d16
- https://www.jenkins.io/security/advisory/2023-06-14/#SECURITY-2932
