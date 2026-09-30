# [H] Improper Input Validation in Jenkins Pipeline: Groovy Plugin

## Summary
Severity: High
Advisory: GHSA-99mf-f3qh-wqrp
CVE: CVE-2020-2109
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-99mf-f3qh-wqrp
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins.workflow:workflow-cps` — affected >=0 <2.79

## Details
Sandbox protection in Jenkins Pipeline: Groovy Plugin 2.78 and earlier can be circumvented through default parameter expressions in CPS-transformed methods.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2109
- https://github.com/jenkinsci/workflow-cps-plugin/commit/41cb4e05eed6a901d0c8a8b0a460111a64c5e179
- https://github.com/jenkinsci/workflow-cps-plugin/commit/90b7f403882e1cab1dec49a011e377f440f8e003
- https://jenkins.io/security/advisory/2020-02-12/#SECURITY-1710
- http://www.openwall.com/lists/oss-security/2020/02/12/3
