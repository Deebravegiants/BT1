# [H] Content-Security-Policy disabled by Red Hat Dependency Analytics Jenkins Plugin

## Summary
Severity: High
Advisory: GHSA-x22x-5pp9-8v7f
CVE: CVE-2024-23905
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-01-24
Source: https://github.com/advisories/GHSA-x22x-5pp9-8v7f
Type: github-advisory

## Affected
- Maven: `io.jenkins.plugins:redhat-dependency-analytics` — affected >=0 <0.9.0

## Details
Jenkins sets the Content-Security-Policy header to static files served by Jenkins (specifically DirectoryBrowserSupport), such as workspaces, /userContent, or archived artifacts, unless a Resource Root URL is specified.

Red Hat Dependency Analytics Plugin 0.7.1 and earlier globally disables the Content-Security-Policy header for static files served by Jenkins whenever the 'Invoke Red Hat Dependency Analytics (RHDA)' build step is executed. This allows cross-site scripting (XSS) attacks by users with the ability to control files in workspaces, archived artifacts, etc.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-23905
- https://github.com/jenkinsci/redhat-dependency-analytics-plugin/commit/123e37795eb69f533a1cd8bd74113ebb1fdbdcda
- https://github.com/jenkinsci/redhat-dependency-analytics-plugin
- https://www.jenkins.io/security/advisory/2024-01-24/#SECURITY-3322
- http://www.openwall.com/lists/oss-security/2024/01/24/6
