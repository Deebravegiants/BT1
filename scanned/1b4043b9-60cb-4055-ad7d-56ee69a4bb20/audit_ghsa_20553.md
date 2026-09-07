# [M] Stored XSS vulnerability in Jenkins Publish Over SSH Plugin

## Summary
Severity: Medium
Advisory: GHSA-fjpm-hf7c-xgc2
CVE: CVE-2022-23110
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-01-13
Source: https://github.com/advisories/GHSA-fjpm-hf7c-xgc2
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:publish-over-ssh` — affected >=0 <1.23

## Details
Jenkins Publish Over SSH Plugin 1.22 and earlier does not escape the SSH server name, resulting in a stored cross-site scripting (XSS) vulnerability exploitable by attackers with Overall/Administer permission.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-23110
- https://github.com/jenkinsci/publish-over-ssh-plugin/commit/edf4e981684326d371200541d440d26b141b269e
- https://github.com/jenkinsci/publish-over-ssh-plugin
- https://github.com/jenkinsci/publish-over-ssh-plugin/releases/tag/publish-over-ssh-1.23
- https://www.jenkins.io/security/advisory/2022-01-12/#SECURITY-2287
- http://www.openwall.com/lists/oss-security/2022/01/12/6
