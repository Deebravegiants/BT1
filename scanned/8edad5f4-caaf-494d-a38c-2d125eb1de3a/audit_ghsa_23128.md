# [M] Missing permission check for paths with specific prefix in Jenkins

## Summary
Severity: Medium
Advisory: GHSA-4625-q52w-39cx
CVE: CVE-2021-21609
CWE: CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-4625-q52w-39cx
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <2.263.2
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.264 <2.275

## Details
Jenkins includes a static list of URLs that are always accessible even without Overall/Read permission, such as the login form. These URLs are excluded from an otherwise universal permission check.

Jenkins 2.274 and earlier, LTS 2.263.1 and earlier does not correctly compare requested URLs with that list.

This allows attackers without Overall/Read permission to access plugin-provided URLs with any of the following prefixes if no other permissions are required:
- `accessDenied`
- `error`
- `instance-identity`
- `login`
- `logout`
- `oops`
- `securityRealm`
- `signup`
- `tcpSlaveAgentListener`

For example, a plugin contributing the path `loginFoo/` would have URLs in that space accessible without the default Overall/Read permission check.

The Jenkins security team is not aware of any affected plugins as of the publication of this advisory.

The comparison of requested URLs with the list of always accessible URLs has been fixed to only allow access to the specific listed URLs in Jenkins 2.275, LTS 2.263.2.

In case this change causes problems, additional paths can be made accessible without Overall/Read permissions: The [Java system property](https://www.jenkins.io/doc/book/managing/system-properties/) `jenkins.model.Jenkins.additionalReadablePaths` is a comma-separated list of additional path prefixes to allow access to.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-21609
- https://github.com/jenkinsci/jenkins/commit/fe9091fc74d55a56fd36544f3038d47c8cb331a4
- https://github.com/jenkinsci/jenkins
- https://www.jenkins.io/security/advisory/2021-01-13/#SECURITY-2047
