# [M] Jenkins Google Cloud Backup Plugin allows attackers with Overall/Read permission to request a manual backup.

## Summary
Severity: Medium
Advisory: GHSA-9xhm-6w5p-335v
CVE: CVE-2022-36917
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-07-28
Source: https://github.com/advisories/GHSA-9xhm-6w5p-335v
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:google-cloud-backup` — affected >=0

## Details
Jenkins Google Cloud Backup Plugin 0.6 and earlier does not perform a permission check in an HTTP endpoint.

This allows attackers with Overall/Read permission to request a manual backup.

Additionally, this HTTP endpoint does not require POST requests, resulting in a cross-site request forgery (CSRF) vulnerability.

As of publication of this advisory, there is no fix.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-36917
- https://www.jenkins.io/security/advisory/2022-07-27/#SECURITY-2656
- http://www.openwall.com/lists/oss-security/2022/07/27/1
