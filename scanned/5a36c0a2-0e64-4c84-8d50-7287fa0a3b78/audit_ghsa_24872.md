# [M] Plaintext Storage of a Password in Jenkins Eagle Tester Plugin

## Summary
Severity: Medium
Advisory: GHSA-vj6f-q4w6-qx9p
CVE: CVE-2020-2129
CWE: CWE-256, CWE-522
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-vj6f-q4w6-qx9p
Type: github-advisory

## Affected
- Maven: `com.mobileenerlytics.eagle.tester:eagle-tester` — affected >=0

## Details
Jenkins Eagle Tester Plugin 1.0.9 and earlier stores a password unencrypted in its global configuration file on the Jenkins master where it can be viewed by users with access to the master file system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2129
- https://jenkins.io/security/advisory/2020-02-12/#SECURITY-1552
- http://www.openwall.com/lists/oss-security/2020/02/12/3
