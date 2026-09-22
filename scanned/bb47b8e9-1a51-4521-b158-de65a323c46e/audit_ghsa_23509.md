# [M] Jenkins GitHub Plugin exposure of sensitive information vulnerability exists

## Summary
Severity: Medium
Advisory: GHSA-v7g7-cmxx-wxw9
CVE: CVE-2018-1000183
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-v7g7-cmxx-wxw9
Type: github-advisory

## Affected
- Maven: `com.coravy.hudson.plugins.github:github` — affected >=0 <1.29.1

## Details
A exposure of sensitive information vulnerability exists in Jenkins GitHub Plugin 1.29.0 and older in GitHubServerConfig.java that allows attackers with Overall/Read access to connect to an attacker-specified URL using attacker-specified credentials IDs obtained through another method, capturing credentials stored in Jenkins.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000183
- https://github.com/jenkinsci/github-plugin/commit/775a8be0d4f7238b33cbbda6508170ff34a90736
- https://github.com/jenkinsci/github-plugin
- https://jenkins.io/security/advisory/2018-06-04/#SECURITY-804
