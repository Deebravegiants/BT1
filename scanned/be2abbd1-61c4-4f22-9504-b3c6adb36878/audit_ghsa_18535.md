# [M] Jenkins Nouvola DiveCloud Plugin vulnerability stores unencrypted credentials

## Summary
Severity: Medium
Advisory: GHSA-45hr-8gq6-7f7f
CVE: CVE-2025-53670
CWE: CWE-312
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-07-09
Source: https://github.com/advisories/GHSA-45hr-8gq6-7f7f
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:nouvola-divecloud` — affected >=0

## Details
Jenkins Nouvola DiveCloud Plugin 1.08 and earlier stores DiveCloud API Keys and Credentials Encryption Keys unencrypted in job config.xml files on the Jenkins controller, where they can be viewed by users with Item/Extended Read permission or access to the Jenkins controller file system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-53670
- https://github.com/jenkinsci/nouvola-divecloud-plugin
- https://www.jenkins.io/security/advisory/2025-07-09/#SECURITY-3526
- http://www.openwall.com/lists/oss-security/2025/07/09/4
