# [M] Jenkins Aqua Security Scanner Plugin vulnerability exposes scanner tokens

## Summary
Severity: Medium
Advisory: GHSA-3wgg-3j4j-3f69
CVE: CVE-2025-53653
CWE: CWE-311, CWE-522
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-07-09
Source: https://github.com/advisories/GHSA-3wgg-3j4j-3f69
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:aqua-security-scanner` — affected >=0

## Details
Jenkins Aqua Security Scanner Plugin 3.2.8 and earlier stores Scanner Tokens for Aqua API unencrypted in job config.xml files on the Jenkins controller as part of its configuration.

These tokens can be viewed by users with Item/Extended Read permission or access to the Jenkins controller file system.

As of publication of this advisory, there is no fix.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-53653
- https://github.com/jenkinsci/aqua-security-scanner-plugin
- https://www.jenkins.io/security/advisory/2025-07-09/#SECURITY-3542
- http://www.openwall.com/lists/oss-security/2025/07/09/4
