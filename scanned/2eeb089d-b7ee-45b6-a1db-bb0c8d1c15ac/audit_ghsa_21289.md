# [H] Content-Security-Policy protection for user content can be disabled in Jenkins 360 FireLine Plugin

## Summary
Severity: High
Advisory: GHSA-7rrj-hqv6-fvpp
CVE: CVE-2022-43435
CWE: CWE-693
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-10-19
Source: https://github.com/advisories/GHSA-7rrj-hqv6-fvpp
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins.plugin:fireline` — affected >=0

## Details
Jenkins sets the Content-Security-Policy header to static files served by Jenkins (specifically `DirectoryBrowserSupport`), such as workspaces, `/userContent`, or archived artifacts, unless a Resource Root URL is specified.

360 FireLine Plugin 1.7.2 and earlier globally disables the `Content-Security-Policy` header for static files served by Jenkins whenever the 'Execute FireLine' build step is executed, if the option 'Open access to HTML with JS or CSS' is checked. This allows cross-site scripting (XSS) attacks by users with the ability to control files in workspaces, archived artifacts, etc.

Jenkins instances with [Resource Root URL](https://www.jenkins.io/doc/book/security/user-content/#resource-root-url) configured are unaffected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-43435
- https://github.com/jenkinsci/fireline-plugin
- https://www.jenkins.io/security/advisory/2022-10-19/#SECURITY-2866
- http://www.openwall.com/lists/oss-security/2022/10/19/3
