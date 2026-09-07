# [H] Stored XSS vulnerability in Jenkins Deployer Framework Plugin

## Summary
Severity: High
Advisory: GHSA-cfvw-84vq-43mx
CVE: CVE-2020-2227
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-cfvw-84vq-43mx
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:deployer-framework` — affected >=0 <1.3

## Details
Deployer Framework Plugin is a framework plugin allowing other plugins to provide a way to deploy artifacts. Deployer Framework Plugin 1.2 and earlier does not escape the URL displayed in the build home page. This results in a stored cross-site scripting (XSS) vulnerability exploitable by users able to provide the location.

The exploitability of this vulnerability depends on the specific implementation using Deployer Framework Plugin. The Jenkins security team is not aware of any exploitable implementation.

Deployer Framework Plugin 1.3 escapes the URL.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2227
- https://github.com/jenkinsci/deployer-framework-plugin/commit/8fa2e16bce85ec1b93be60102d7cfb5153876e83
- https://github.com/jenkinsci/deployer-framework-plugin
- https://jenkins.io/security/advisory/2020-07-15/#SECURITY-1915
- http://www.openwall.com/lists/oss-security/2020/07/15/5
