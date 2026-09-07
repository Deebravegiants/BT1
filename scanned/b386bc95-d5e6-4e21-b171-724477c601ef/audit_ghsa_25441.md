# [H] CSRF vulnerability in Jenkins Configuration Slicing Plugin

## Summary
Severity: High
Advisory: GHSA-42mm-x828-56c7
CVE: CVE-2021-21617
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-42mm-x828-56c7
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:configurationslicing` — affected >=0 <1.52

## Details
Jenkins Configuration Slicing Plugin 1.51 and earlier does not require POST requests for the form submission endpoint reconfiguring slices, resulting in a cross-site request forgery (CSRF) vulnerability.

This vulnerability allows attackers to apply different slice configurations to attacker-specified jobs.

Jenkins Configuration Slicing Plugin 1.52 requires POST requests for the affected HTTP endpoint.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-21617
- https://github.com/jenkinsci/configurationslicing-plugin/commit/b22b82df3654e8379466a51de4391884aa4d6156
- https://github.com/jenkinsci/configurationslicing-plugin
- https://www.jenkins.io/security/advisory/2021-02-24/#SECURITY-2003
- http://www.openwall.com/lists/oss-security/2021/02/24/3
