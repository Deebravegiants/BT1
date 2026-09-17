# [M] Jenkins AppSpider Plugin  missing permission checks

## Summary
Severity: Medium
Advisory: GHSA-xxv9-w5hm-328j
CVE: CVE-2024-28155
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-03-06
Source: https://github.com/advisories/GHSA-xxv9-w5hm-328j
Type: github-advisory

## Affected
- Maven: `com.rapid7:jenkinsci-appspider-plugin` — affected >=0 <1.0.17

## Details
Jenkins AppSpider Plugin 1.0.16 and earlier does not perform permission checks in several HTTP endpoints, allowing attackers with Overall/Read permission to obtain information about available scan config names, engine group names, and client names.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-28155
- https://github.com/jenkinsci/appspider-build-scanner-plugin/commit/1677f098fbe4c71d782fc4c7bab5f972c575a86d
- https://github.com/jenkinsci/appspider-build-scanner-plugin
- https://www.jenkins.io/security/advisory/2024-03-06/#SECURITY-3144
- http://www.openwall.com/lists/oss-security/2024/03/06/3
