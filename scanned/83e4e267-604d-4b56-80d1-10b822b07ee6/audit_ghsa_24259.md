# [H] RCE vulnerability in Jenkins Azure Container Service Plugin

## Summary
Severity: High
Advisory: GHSA-5qff-7944-vq4f
CVE: CVE-2020-2168
CWE: CWE-20, CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-5qff-7944-vq4f
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:azure-acs` — affected >=0 <1.0.2

## Details
Azure Container Service Plugin 1.0.1 and earlier does not configure its YAML parser to prevent the instantiation of arbitrary types. This results in a remote code execution (RCE) vulnerability exploitable by users able to provide YAML input files to Azure Container Service Plugin’s build step.

Azure Container Service Plugin 1.0.2 configures its YAML parser to only instantiate safe types.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2168
- https://github.com/jenkinsci/azure-acs-plugin
- https://jenkins.io/security/advisory/2020-03-25/#SECURITY-1732
- http://www.openwall.com/lists/oss-security/2020/03/25/2
