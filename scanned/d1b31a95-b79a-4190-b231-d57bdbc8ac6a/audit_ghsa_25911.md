# [H] XML External Entity Reference vulnerability in Jenkins Pipeline: Phoenix AutoTest Plugin

## Summary
Severity: High
Advisory: GHSA-rwg2-w82x-v57j
CVE: CVE-2022-28155
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2022-03-30
Source: https://github.com/advisories/GHSA-rwg2-w82x-v57j
Type: github-advisory

## Affected
- Maven: `com.surenpi.jenkins:phoenix-autotest` — affected >=0

## Details
Jenkins Pipeline: Phoenix AutoTest Plugin 1.3 and earlier does not configure its XML parser to prevent XML external entity (XXE) attacks.
This allows attackers able to control the input files for the `readXml` or `writeXml` build step to have Jenkins parse a crafted file that uses external entities for extraction of secrets from the Jenkins controller or server-side request forgery.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-28155
- https://github.com/jenkinsci/phoenix-autotest-plugin
- https://www.jenkins.io/security/advisory/2022-03-29/#SECURITY-1897
- http://www.openwall.com/lists/oss-security/2022/03/29/1
