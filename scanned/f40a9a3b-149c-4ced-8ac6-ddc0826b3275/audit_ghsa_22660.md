# [M] Missing Authorization in Jenkins Configuration as Code Plugin

## Summary
Severity: Medium
Advisory: GHSA-mqr8-3v8j-46wv
CVE: CVE-2019-10344
CWE: CWE-285, CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-mqr8-3v8j-46wv
Type: github-advisory

## Affected
- Maven: `io.jenkins:configuration-as-code` — affected >=0 <1.25

## Details
Missing permission checks in Jenkins Configuration as Code Plugin 1.24 and earlier in various HTTP endpoints allowed users with Overall/Read access to access the generated schema and documentation for this plugin containing detailed information about installed plugins.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10344
- https://github.com/jenkinsci/configuration-as-code-plugin/commit/1c531c1a46fc1da6a82cd728bf66428083d30fef
- https://jenkins.io/security/advisory/2019-07-31/#SECURITY-1290
- http://www.openwall.com/lists/oss-security/2019/07/31/1
