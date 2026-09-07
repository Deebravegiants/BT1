# [M] Missing permission checks in SSH Agent Plugin allow enumerating credentials IDs

## Summary
Severity: Medium
Advisory: GHSA-9wxh-jjj5-67cv
CVE: CVE-2022-20620
CWE: CWE-668, CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-01-13
Source: https://github.com/advisories/GHSA-9wxh-jjj5-67cv
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:ssh-agent` — affected >=1.23 <1.23.2
- Maven: `org.jenkins-ci.plugins:ssh-agent` — affected >=0 <1.22.1

## Details
Jenkins SSH Agent Plugin prior to 1.23.2 and 1.22.1 does not perform permission checks in several HTTP endpoints.

This allows attackers with Overall/Read access to enumerate credentials IDs of credentials stored in Jenkins. Those can be used as part of an attack to capture the credentials using another vulnerability.

An enumeration of credentials IDs in SSH Agent Plugin 1.23.2 and 1.22.1 requires the appropriate permissions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-20620
- https://github.com/jenkinsci/ssh-agent-plugin/commit/04f526d2f73a6fc24b59df20ba03d95265114835
- https://github.com/jenkinsci/ssh-agent-plugin/commit/9c08b9f93cfb3ada0f0124f5bd7f0d027728a750
- https://github.com/CVEProject/cvelist/blob/2d78eb36f4d084db7fb35f1535d8d84fdcb7d859/2022/20xxx/CVE-2022-20620.jsonhttps://github.com/CVEProject/cvelist/blob/2d78eb36f4d084db7fb35f1535d8d84fdcb7d859/2022/20xxx/CVE-2022-20620.json
- https://github.com/jenkinsci/ssh-agent-plugin
- https://www.jenkins.io/security/advisory/2022-01-12/#SECURITY-2189
- http://www.openwall.com/lists/oss-security/2022/01/12/6
