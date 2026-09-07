# [H] Content-Security-Policy protection for user content disabled by Jenkins XFramium Builder Plugin

## Summary
Severity: High
Advisory: GHSA-px4x-hjm5-w8x3
CVE: CVE-2022-43432
CWE: CWE-693
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-10-19
Source: https://github.com/advisories/GHSA-px4x-hjm5-w8x3
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:xframium` — affected >=0

## Details
Jenkins sets the Content-Security-Policy header to static files served by Jenkins (specifically `DirectoryBrowserSupport`), such as workspaces, `/userContent`, or archived artifacts, unless a Resource Root URL is specified.

XFramium Builder Plugin 1.0.22 and earlier globally disables the `Content-Security-Policy` header for static files served by Jenkins as soon as it is loaded. This allows cross-site scripting (XSS) attacks by users with the ability to control files in workspaces, archived artifacts, etc.

Jenkins instances with [Resource Root URL](https://www.jenkins.io/doc/book/security/user-content/#resource-root-url) configured are unaffected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-43432
- https://github.com/jenkinsci/xframium-plugin
- https://www.jenkins.io/security/advisory/2022-10-19/#SECURITY-2863
- http://www.openwall.com/lists/oss-security/2022/10/19/3
