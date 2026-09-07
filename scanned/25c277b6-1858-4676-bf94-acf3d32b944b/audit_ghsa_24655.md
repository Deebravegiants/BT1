# [H] CSRF vulnerability in Jenkins warnings Plugin allows remote code execution

## Summary
Severity: High
Advisory: GHSA-q564-vvx8-9388
CVE: CVE-2020-2280
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-q564-vvx8-9388
Type: github-advisory

## Affected
- Maven: `org.jvnet.hudson.plugins:warnings` — affected >=0 <5.0.2

## Details
warnings Plugin 5.0.1 and earlier does not require POST requests for a form validation method intended for testing custom warnings parsers, resulting in a cross-site request forgery (CSRF) vulnerability.

This vulnerability allows attackers to execute arbitrary code.

warnings Plugin 5.0.2 requires POST requests for the affected form validation method.

This vulnerability was caused by an incomplete fix to [SECURITY-1295](https://www.jenkins.io/security/advisory/2019-01-28/).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2280
- https://github.com/jenkinsci/warnings-plugin
- https://www.jenkins.io/security/advisory/2020-09-23/#SECURITY-2042
- http://www.openwall.com/lists/oss-security/2020/09/23/1
