# [M] Incorrect control flow in Jenkins Gradle Plugin breaks credentials masking in the build log

## Summary
Severity: Medium
Advisory: GHSA-pvjf-4hfg-wr84
CVE: CVE-2023-39152
CWE: CWE-670
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-07-26
Source: https://github.com/advisories/GHSA-pvjf-4hfg-wr84
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:gradle` — affected >=0 <2.8.1

## Details
Always-incorrect control flow implementation in Jenkins Gradle Plugin 2.8 may result in credentials not being masked (i.e., replaced with asterisks) in the build log in some circumstances.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-39152
- https://www.jenkins.io/security/advisory/2023-07-26/#SECURITY-3208
- http://www.openwall.com/lists/oss-security/2023/07/26/2
