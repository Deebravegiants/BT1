# [M] Stored XSS vulnerability in Jenkins RapidDeploy Plugin

## Summary
Severity: Medium
Advisory: GHSA-f4gq-7hvf-fjm3
CVE: CVE-2020-2170
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-f4gq-7hvf-fjm3
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:rapiddeploy-jenkins` — affected >=0 <4.2.1

## Details
RapidDeploy Plugin 4.2 and earlier does not escape package names in its displayed table of packages obtained from a remote server. This results in a stored cross-site scripting (XSS) vulnerability exploitable by users able to configure jobs.

RapidDeploy Plugin 4.2.1 escapes package names.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2170
- https://github.com/jenkinsci/rapiddeploy-plugin
- https://jenkins.io/security/advisory/2020-03-25/#SECURITY-1676
- http://www.openwall.com/lists/oss-security/2020/03/25/2
