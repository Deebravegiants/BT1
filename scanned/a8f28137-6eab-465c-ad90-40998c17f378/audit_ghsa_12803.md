# [M] Cisco Spark Notifier Jenkins Plugin contains Missing Authorization

## Summary
Severity: Medium
Advisory: GHSA-hcvf-pfrm-jxgf
CVE: CVE-2023-24451
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-01-26
Source: https://github.com/advisories/GHSA-hcvf-pfrm-jxgf
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:cisco-spark-notifier-plugin` — affected >=0

## Details
A missing permission check in Jenkins Cisco Spark Notifier Plugin 1.1.1 and earlier allows attackers with Overall/Read permission to enumerate credentials IDs of credentials stored in Jenkins.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-24451
- https://github.com/jenkinsci/cisco-spark-notifier-plugin
- https://www.jenkins.io/security/advisory/2023-01-24/#SECURITY-2803
