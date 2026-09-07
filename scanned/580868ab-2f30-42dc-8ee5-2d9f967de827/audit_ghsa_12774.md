# [M] Plaintext Storage of a Password in Jenkins TestQuality Updater Plugin

## Summary
Severity: Medium
Advisory: GHSA-98qc-v8vg-mcx4
CVE: CVE-2023-24454
CWE: CWE-256, CWE-312
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-01-26
Source: https://github.com/advisories/GHSA-98qc-v8vg-mcx4
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:testquality-updater` — affected >=0

## Details
Jenkins TestQuality Updater Plugin 1.3 and earlier stores the TestQuality Updater password unencrypted in its global configuration file on the Jenkins controller where it can be viewed by users with access to the Jenkins controller file system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-24454
- https://www.jenkins.io/security/advisory/2023-01-24/#SECURITY-2091
