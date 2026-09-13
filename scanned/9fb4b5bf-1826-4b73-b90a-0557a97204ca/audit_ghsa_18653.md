# [M] Jenkins ByteGuard Build Actions Plugin stores API tokens unencrypted in job config.xml files

## Summary
Severity: Medium
Advisory: GHSA-2vmr-8c82-x8xq
CVE: CVE-2025-64144
CWE: CWE-311
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-10-29
Source: https://github.com/advisories/GHSA-2vmr-8c82-x8xq
Type: github-advisory

## Affected
- Maven: `io.jenkins.plugins:byteguard-build-actions` — affected >=0

## Details
Jenkins ByteGuard Build Actions Plugin 1.0 and earlier stores API tokens unencrypted in job `config.xml` files on the Jenkins controller as part of its configuration.

These tokens can be viewed by users with Item/Extended Read permission or access to the Jenkins controller file system.

Additionally, the job configuration form does not mask these credentials, increasing the potential for attackers to observe and capture them.

As of publication of this advisory, there is no fix.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-64144
- https://github.com/jenkinsci/byteguard-build-actions-plugin
- https://www.jenkins.io/security/advisory/2025-10-29/#SECURITY-3560
- http://www.openwall.com/lists/oss-security/2025/10/29/2
