# [M] Jenkins Nouvola DiveCloud Plugin vulnerability does not mask keys on its job configuration form

## Summary
Severity: Medium
Advisory: GHSA-4v4v-92cx-x4f4
CVE: CVE-2025-53671
CWE: CWE-256
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-07-09
Source: https://github.com/advisories/GHSA-4v4v-92cx-x4f4
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:nouvola-divecloud` — affected >=0

## Details
Jenkins Nouvola DiveCloud Plugin 1.08 and earlier does not mask DiveCloud API Keys and Credentials Encryption Keys displayed on the job configuration form, increasing the potential for attackers to observe and capture them.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-53671
- https://github.com/jenkinsci/nouvola-divecloud-plugin
- https://www.jenkins.io/security/advisory/2025-07-09/#SECURITY-3526
- http://www.openwall.com/lists/oss-security/2025/07/09/4
