# [H] Complete lack of CSRF protection in Jenkins Selenium Plugin can lead to OS command injection

## Summary
Severity: High
Advisory: GHSA-rp4x-xpgf-4xv7
CVE: CVE-2020-2196
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-rp4x-xpgf-4xv7
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:selenium` — affected >=0

## Details
Selenium Plugin 3.141.59 and earlier has no CSRF protection for its HTTP endpoints.

This allows attackers to perform the following actions:
- Restart the Selenium Grid hub.
- Delete or replace the plugin configuration.
- Start, stop, or restart Selenium configurations on specific nodes.

Through carefully chosen configuration parameters, these actions can result in OS command injection on the Jenkins controller.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2196
- https://github.com/jenkinsci/selenium-plugin
- https://jenkins.io/security/advisory/2020-06-03/#SECURITY-1766
- http://www.openwall.com/lists/oss-security/2020/06/03/3
- http://www.openwall.com/lists/oss-security/2022/04/14/2
