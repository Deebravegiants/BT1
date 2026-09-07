# [M] Jenkins Cluster Statistics Plugin Missing Authorization vulnerability

## Summary
Severity: Medium
Advisory: GHSA-w8wg-62wf-62gm
CVE: CVE-2022-45399
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-11-16
Source: https://github.com/advisories/GHSA-w8wg-62wf-62gm
Type: github-advisory

## Affected
- Maven: `org.zeroturnaround:cluster-stats` — affected >=0

## Details
Jenkins Cluster Statistics Plugin 0.4.6 and earlier does not perform a permission check in an HTTP endpoint.

This allows attackers with Overall/Read permission to delete recorded Jenkins Cluster Statistics.

Additionally, this HTTP endpoint does not require POST requests, resulting in a cross-site request forgery (CSRF) vulnerability.

As of publication of this advisory, there is no fix.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-45399
- https://www.jenkins.io/security/advisory/2022-11-15/#SECURITY-2938
- http://www.openwall.com/lists/oss-security/2022/11/15/4
