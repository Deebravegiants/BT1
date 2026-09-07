# [M] Content-Security-Policy protection for user content disabled by Jenkins ZAP Pipeline Plugin

## Summary
Severity: Medium
Advisory: GHSA-4c87-9xq5-5c35
CVE: CVE-2020-2214
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-4c87-9xq5-5c35
Type: github-advisory

## Affected
- Maven: `com.vrondakis.zap:zap-pipeline` — affected >=0 <1.10

## Details
Jenkins sets the `Content-Security-Policy` header to static files served by Jenkins (specifically `DirectoryBrowserSupport`), such as workspaces, `/userContent`, or archived artifacts.

ZAP Pipeline Plugin prior to 1.10 globally disables the `Content-Security-Policy` header for static files served by Jenkins. This allows cross-site scripting (XSS) attacks by users with the ability to control files in workspaces, archived artifacts, etc.

Jenkins instances with [Resource Root URL](https://www.jenkins.io/doc/upgrade-guide/2.204/#resource-domain-support) configured are largely unaffected. A possible exception are file parameter downloads. The behavior of those depends on the specific version of Jenkins:
- Jenkins 2.231 and newer, including 2.235.x LTS, is unaffected, as all resource files from user content are generally served safely from a different domain, without restrictions from `Content-Security-Policy` header.
- Jenkins between 2.228 (inclusive) and 2.230 (inclusive), as well as all releases of Jenkins 2.222.x LTS and the 2.204.6 LTS release, are affected by this vulnerability, as file parameters are not served via the Resource Root URL.
- Jenkins 2.227 and older, 2.204.5 and older, don’t have XSS protection for file parameter values, see [SECURITY-1793](https://www.jenkins.io/security/advisory/2020-03-25/#SECURITY-1793).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2214
- https://github.com/jenkinsci/zap-pipeline-plugin/commit/bca4b087c66ead39398f54cdadc27c515e8ede31
- https://github.com/jenkinsci/zap-pipeline-plugin
- https://jenkins.io/security/advisory/2020-07-02/#SECURITY-1811
- http://www.openwall.com/lists/oss-security/2020/07/02/7
