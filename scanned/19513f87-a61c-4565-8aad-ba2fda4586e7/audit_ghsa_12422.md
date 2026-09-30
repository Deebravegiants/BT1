# [M] Missing permission check in Jenkins Scriptler Plugin

## Summary
Severity: Medium
Advisory: GHSA-4j42-6xfx-h754
CVE: CVE-2023-50765
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-12-13
Source: https://github.com/advisories/GHSA-4j42-6xfx-h754
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:scriptler` — affected >=0

## Details
A missing permission check in Jenkins Scriptler Plugin 342.v6a_89fd40f466 and earlier allows attackers with Overall/Read permission to read the contents of a Groovy script by knowing its ID.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-50765
- https://github.com/jenkinsci/scriptler-plugin/commit/5addb5f9e68596abdba216e61cf714c2767b874b
- https://github.com/jenkinsci/scriptler-plugin
- https://www.jenkins.io/security/advisory/2023-12-13/#SECURITY-3206
- http://www.openwall.com/lists/oss-security/2023/12/13/4
