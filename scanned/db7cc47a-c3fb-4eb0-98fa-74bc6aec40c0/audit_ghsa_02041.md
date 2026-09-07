# [M] Cross-site scripting in Jenkins Kiuwan Plugin

## Summary
Severity: Medium
Advisory: GHSA-8h77-3xwr-hqhh
CVE: CVE-2021-21666
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-06-16
Source: https://github.com/advisories/GHSA-8h77-3xwr-hqhh
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:kiuwanJenkinsPlugin` — affected >=0 <1.6.1

## Details
Jenkins Kiuwan Plugin 1.6.0 and earlier does not escape query parameters in an error message for a form validation endpoint, resulting in a reflected cross-site scripting (XSS) vulnerability.

Only older releases of Jenkins are affected by this vulnerability. Jenkins 2.275 and newer, LTS 2.263.2 and newer include a protection preventing this from being exploitable.

Jenkins Kiuwan Plugin 1.6.1 escapes affected parts of the error message in the form validation endpoint.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-21666
- https://github.com/jenkinsci/kiuwan-plugin/commit/a5f6fdb1b8ad09d170547a4cc2b90c4829ef1f0a
- https://github.com/jenkinsci/kiuwan-plugin
- https://www.jenkins.io/security/advisory/2021-06-10/#SECURITY-2367
- http://www.openwall.com/lists/oss-security/2021/06/10/14
