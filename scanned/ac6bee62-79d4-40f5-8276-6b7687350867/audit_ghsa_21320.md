# [H] Content-Security-Policy protection for user content disabled by Jenkins ScreenRecorder Plugin

## Summary
Severity: High
Advisory: GHSA-cvxj-4745-843x
CVE: CVE-2022-43433
CWE: CWE-693
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-10-19
Source: https://github.com/advisories/GHSA-cvxj-4745-843x
Type: github-advisory

## Affected
- Maven: `io.jenkins.plugins:screenrecorder` — affected >=0

## Details
Jenkins sets the `Content-Security-Policy` header to static files served by Jenkins (specifically `DirectoryBrowserSupport`), such as workspaces, `/userContent`, or archived artifacts, unless a Resource Root URL is specified.

ScreenRecorder Plugin 0.7 and earlier programmatically updates [the Java system property](https://www.jenkins.io/doc/book/managing/system-properties/#hudson-model-directorybrowsersupport-csp) allowing administrators to customize the `Content-Security-Policy` header for static files served by Jenkins to include `media-src: 'self'`. On a Jenkins instance with default configuration, this effectively disables all other directives in the default rule set, including `script-src`. This allows cross-site scripting (XSS) attacks by users with the ability to control files in workspaces, archived artifacts, etc.

Jenkins instances with [Resource Root URL](https://www.jenkins.io/doc/book/security/user-content/#resource-root-url) configured are unaffected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-43433
- https://github.com/jenkinsci/screenrecorder-plugin
- https://www.jenkins.io/security/advisory/2022-10-19/#SECURITY-2864
- http://www.openwall.com/lists/oss-security/2022/10/19/3
