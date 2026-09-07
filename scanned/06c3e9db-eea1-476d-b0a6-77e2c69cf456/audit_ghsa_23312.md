# [M] CSRF vulnerability in MongoDB Plugin

## Summary
Severity: Medium
Advisory: GHSA-j6p9-hm3q-hwmj
CVE: CVE-2020-2268
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-j6p9-hm3q-hwmj
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:mongodb` — affected >=0

## Details
Jenkins MongoDB Plugin 1.3 and earlier does not perform permission checks in methods implementing form validation.

This allows attackers with Overall/Read permission to gain access to some metadata of any arbitrary files on the Jenkins controller.

Additionally, these form validation methods do not require POST requests, resulting in a cross-site request forgery (CSRF) vulnerability.

As of publication of this advisory, there is no fix.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2268
- https://github.com/jenkinsci/mongodb-plugin
- https://www.jenkins.io/security/advisory/2020-09-16/#SECURITY-1904
- http://www.openwall.com/lists/oss-security/2020/09/16/3
