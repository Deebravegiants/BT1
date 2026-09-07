# [M] Stored Cross-site Scripting vulnerability in Jenkins global-build-stats Plugin

## Summary
Severity: Medium
Advisory: GHSA-wj78-8xrx-phr7
CVE: CVE-2022-27207
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-03-16
Source: https://github.com/advisories/GHSA-wj78-8xrx-phr7
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:global-build-stats` — affected >=0

## Details
Jenkins global-build-stats Plugin 1.5 and earlier does not escape multiple fields in the chart configuration on the 'Global Build Stats' page, resulting in a stored cross-site scripting (XSS) vulnerability exploitable by attackers with Overall/Administer permission.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-27207
- https://github.com/jenkinsci/global-build-stats-plugin/commit/214f74360b3a91734b6e2a4b281ff0086a1e0679
- https://github.com/jenkinsci/global-build-stats-plugin
- https://www.jenkins.io/security/advisory/2022-03-15/#SECURITY-1886
- http://www.openwall.com/lists/oss-security/2022/03/15/2
