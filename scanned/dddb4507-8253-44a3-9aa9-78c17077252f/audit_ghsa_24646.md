# [H] RCE vulnerability in Jenkins Yaml Axis Plugin

## Summary
Severity: High
Advisory: GHSA-324h-2v7h-q3xx
CVE: CVE-2020-2179
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-324h-2v7h-q3xx
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:yaml-axis` — affected >=0 <0.2.1

## Details
Yaml Axis Plugin 0.2.0 and earlier does not configure its YAML parser to prevent the instantiation of arbitrary types. This results in a remote code execution (RCE) vulnerability exploitable by users able to configure a multi-configuration (Matrix) job, or control the contents of a previously configured job’s SCM repository.

Yaml Axis Plugin 0.2.1 configures its YAML parser to only instantiate safe types.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2179
- https://github.com/jenkinsci/yaml-axis-plugin/commit/346802860c68a5a9bb4996c81fed4e05bee594f4
- https://github.com/jenkinsci/yaml-axis-plugin
- https://jenkins.io/security/advisory/2020-04-16/#SECURITY-1825
- http://www.openwall.com/lists/oss-security/2020/04/16/4
