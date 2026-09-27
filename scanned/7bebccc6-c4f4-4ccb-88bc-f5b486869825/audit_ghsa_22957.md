# [M] Exposure of Sensitive Information in Jenkins Kubernetes Plugin

## Summary
Severity: Medium
Advisory: GHSA-v67x-gpg7-mwv3
CVE: CVE-2018-1000187
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-v67x-gpg7-mwv3
Type: github-advisory

## Affected
- Maven: `org.csanchez.jenkins.plugins:kubernetes` — affected >=0 <1.7.1

## Details
A exposure of sensitive information vulnerability exists in Jenkins Kubernetes Plugin 1.7.0 and older in ContainerExecDecorator.java that results in sensitive variables such as passwords being written to logs.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000187
- https://github.com/jenkinsci/kubernetes-plugin/commit/43a1d15b0875ae89ae16f2a2bfdd44ffd1e5f46d
- https://jenkins.io/security/advisory/2018-06-04/#SECURITY-883
- https://www.jenkins.io/security/advisory/2018-06-04/#SECURITY-883
