# [M] Jenkins Report Portal Plugin allows users with Item/Extended Read permission to view tokens on Jenkins controller

## Summary
Severity: Medium
Advisory: GHSA-qgw9-vgrf-h723
CVE: CVE-2023-30523
CWE: CWE-312
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-04-12
Source: https://github.com/advisories/GHSA-qgw9-vgrf-h723
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:reportportal` — affected >=0

## Details
Jenkins Report Portal Plugin 0.5 and earlier stores ReportPortal access tokens unencrypted in job `config.xml` files on the Jenkins controller as part of its configuration.

These tokens can be viewed by users with Item/Extended Read permission or access to the Jenkins controller file system.

Additionally, the configuration form does not mask these tokens, increasing the potential for attackers to observe and capture them.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-30523
- https://www.jenkins.io/security/advisory/2023-04-12/#SECURITY-2945
- http://www.openwall.com/lists/oss-security/2023/04/13/3
