# [M] Jenkins GitHub Plugin server-side request forgery vulnerability exists

## Summary
Severity: Medium
Advisory: GHSA-gh85-mq87-r7v3
CVE: CVE-2018-1000184
CWE: CWE-918
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-gh85-mq87-r7v3
Type: github-advisory

## Affected
- Maven: `com.coravy.hudson.plugins.github:github` — affected >=0 <1.29.1

## Details
A server-side request forgery vulnerability exists in Jenkins GitHub Plugin 1.29.0 and older in GitHubPluginConfig.java that allows attackers with Overall/Read access to cause Jenkins to send a GET request to a specified URL.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000184
- https://github.com/jenkinsci/github-plugin/commit/9a20b7d74ec1bfa8afe260571485dec286b454a2
- https://github.com/jenkinsci/github-plugin
- https://jenkins.io/security/advisory/2018-06-04/#SECURITY-799
