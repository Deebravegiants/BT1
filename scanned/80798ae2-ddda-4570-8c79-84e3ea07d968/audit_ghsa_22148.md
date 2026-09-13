# [H] Stored credentials unencrypted in Jenkins Mashup Portlets Plugin

## Summary
Severity: High
Advisory: GHSA-9p5v-6p5f-f28h
CVE: CVE-2019-10347
CWE: CWE-522
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-9p5v-6p5f-f28h
Type: github-advisory

## Affected
- Maven: `javagh.jenkins:mashup-portlets-plugin` — affected >=0 <1.1.0

## Details
Jenkins Mashup Portlets Plugin stored credentials unencrypted on the Jenkins master where they can be viewed by users with access to the master file system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10347
- https://github.com/jenkinsci/mashup-portlets-plugin/commit/05eb9bfd5c758c8c477ce6bd4315fd65d83e9a0a
- https://jenkins.io/security/advisory/2019-07-11/#SECURITY-775
- http://www.openwall.com/lists/oss-security/2019/07/11/4
- http://www.securityfocus.com/bid/109156
