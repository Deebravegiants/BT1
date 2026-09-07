# [H] Content-Security-Policy protection for user content disabled by Jenkins NeuVector Vulnerability Scanner Plugin

## Summary
Severity: High
Advisory: GHSA-wmfh-h3vm-rcxm
CVE: CVE-2022-43434
CWE: CWE-693
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-10-19
Source: https://github.com/advisories/GHSA-wmfh-h3vm-rcxm
Type: github-advisory

## Affected
- Maven: `io.jenkins.plugins:neuvector-vulnerability-scanner` — affected >=0 <1.22

## Details
Jenkins sets the Content-Security-Policy header to static files served by Jenkins (specifically `DirectoryBrowserSupport`), such as workspaces, `/userContent`, or archived artifacts, unless a Resource Root URL is specified.

NeuVector Vulnerability Scanner Plugin 1.20 and earlier globally disables the `Content-Security-Policy` header for static files served by Jenkins whenever the 'NeuVector Vulnerability Scanner' build step is executed. This allows cross-site scripting (XSS) attacks by users with the ability to control files in workspaces, archived artifacts, etc.

Jenkins instances with [Resource Root URL](https://www.jenkins.io/doc/book/security/user-content/#resource-root-url) configured are unaffected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-43434
- https://github.com/jenkinsci/neuvector-vulnerability-scanner-plugin/commit/e0a72373ef1c20c41b8eb086883a7090cf04809c
- https://github.com/jenkinsci/neuvector-vulnerability-scanner-plugin
- https://www.jenkins.io/security/advisory/2022-10-19/#SECURITY-2865
- http://www.openwall.com/lists/oss-security/2022/10/19/3
