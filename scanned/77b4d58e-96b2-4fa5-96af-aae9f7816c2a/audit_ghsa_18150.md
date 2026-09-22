# [M] Jenkins global-build-stats Plugin missing permission check can result in graph IDs being enumerated

## Summary
Severity: Medium
Advisory: GHSA-gm8g-fh49-qq6v
CVE: CVE-2025-58459
CWE: CWE-284
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-09-03
Source: https://github.com/advisories/GHSA-gm8g-fh49-qq6v
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:global-build-stats` — affected >=0 <347.v32a

## Details
Jenkins global-build-stats Plugin 322.v22f4db_18e2dd and earlier does not perform permission checks in its REST API endpoints, allowing attackers with Overall/Read permission to enumerate graph IDs. 

This has been patched in version 347.v32a_eb_0493c4f.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-58459
- https://github.com/jenkinsci/global-build-stats-plugin/commit/32aeb0493c4ff5423448576f477ac612f7a25138
- https://github.com/jenkinsci/global-build-stats-plugin
- https://www.jenkins.io/security/advisory/2025-09-03/#SECURITY-3535
- http://www.openwall.com/lists/oss-security/2025/09/03/4
