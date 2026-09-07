# [M] Stored XSS vulnerability in Jenkins Release Plugin

## Summary
Severity: Medium
Advisory: GHSA-vmg8-g8j3-m355
CVE: CVE-2020-2292
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-vmg8-g8j3-m355
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:release` — affected >=0 <2.11

## Details
Jenkins Release Plugin 2.10.2 and earlier does not escape the release version in badge tooltip, resulting in a stored cross-site scripting (XSS) vulnerability exploitable by attackers with Release/Release permission.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2292
- https://github.com/jenkinsci/release-plugin/commit/99814a0c82f5edf34ad297c2e98af9315bc6b5c2
- https://github.com/jenkinsci/release-plugin
- https://www.jenkins.io/security/advisory/2020-10-08/#SECURITY-1928
- http://www.openwall.com/lists/oss-security/2020/10/08/5
