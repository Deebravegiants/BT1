# [M] Cross-Site Request Forgery in Jenkins Cluster Statistics Plugin

## Summary
Severity: Medium
Advisory: GHSA-24hp-84jp-8wgm
CVE: CVE-2022-45398
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-11-16
Source: https://github.com/advisories/GHSA-24hp-84jp-8wgm
Type: github-advisory

## Affected
- Maven: `org.zeroturnaround:cluster-stats` — affected >=0

## Details
A cross-site request forgery (CSRF) vulnerability in Jenkins Cluster Statistics Plugin 0.4.6 and earlier allows attackers to delete recorded Jenkins Cluster Statistics.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-45398
- https://github.com/jenkinsci/cluster-stats-plugin
- https://www.jenkins.io/security/advisory/2022-11-15/#SECURITY-2938
- http://www.openwall.com/lists/oss-security/2022/11/15/4
