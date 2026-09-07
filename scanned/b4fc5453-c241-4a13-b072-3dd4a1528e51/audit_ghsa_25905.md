# [H] Cross-site Scripting (XSS) vulnerability in Jenkins Continuous Integration with Toad Edge Plugin

## Summary
Severity: High
Advisory: GHSA-7jh8-ghwc-82cw
CVE: CVE-2022-28145
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-03-30
Source: https://github.com/advisories/GHSA-7jh8-ghwc-82cw
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:ci-with-toad-edge` — affected >=0 <2.4

## Details
Jenkins Continuous Integration with Toad Edge Plugin 2.3 and earlier does not apply Content-Security-Policy headers to report files it serves, resulting in a stored cross-site scripting (XSS) exploitable by attackers with Item/Configure permission or otherwise able to control report contents.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-28145
- https://github.com/jenkinsci/ci-with-toad-edge-plugin/commit/d6b2292949d0cddf4a2981fefbf3e30d1dfcd88a
- https://github.com/jenkinsci/ci-with-toad-edge-plugin
- https://www.jenkins.io/security/advisory/2022-03-29/#SECURITY-1892
- http://www.openwall.com/lists/oss-security/2022/03/29/1
