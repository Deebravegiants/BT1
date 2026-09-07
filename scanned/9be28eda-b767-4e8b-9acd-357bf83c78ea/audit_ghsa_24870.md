# [H] RCE vulnerability in ElasticBox Jenkins Kubernetes CI/CD Plugin

## Summary
Severity: High
Advisory: GHSA-9r3h-wm3x-v245
CVE: CVE-2020-2211
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-9r3h-wm3x-v245
Type: github-advisory

## Affected
- Maven: `com.elasticbox.jenkins-ci.plugins:kubernetes-ci` — affected >=0

## Details
ElasticBox Jenkins Kubernetes CI/CD Plugin 1.3 and earlier does not configure its YAML parser to prevent the instantiation of arbitrary types. This results in a remote code execution (RCE) vulnerability exploitable by users able to provide YAML input files to ElasticBox Jenkins Kubernetes CI/CD Plugin’s build step.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2211
- https://github.com/jenkinsci/kubernetes-ci-plugin
- https://jenkins.io/security/advisory/2020-07-02/#SECURITY-1738
- http://www.openwall.com/lists/oss-security/2020/07/02/7
