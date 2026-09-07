# [H] Jenkins Deploy WebLogic Plugin cross-site request forgery vulnerability

## Summary
Severity: High
Advisory: GHSA-6x2w-gwgf-5rg3
CVE: CVE-2019-10464
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-6x2w-gwgf-5rg3
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:weblogic-deployer-plugin` — affected >=0

## Details
JenkinsDeploy WebLogic Plugin does not perform permission checks on a method implementing form validation. This allows users with Overall/Read access to Jenkins to send an HTTP HEAD request to a user-specified URL, or confirm the existence of any file or directory on the Jenkins controller.

Additionally, the form validation method does not require POST requests, resulting in a CSRF vulnerability.

As of publication of this advisory, there is no fix.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10464
- https://jenkins.io/security/advisory/2019-10-23/#SECURITY-820
- http://www.openwall.com/lists/oss-security/2019/10/23/2
