# [M] Jenkins Data Theorem Mobile Security: CI/CD Plugin has Insufficiently Protected Credentials

## Summary
Severity: Medium
Advisory: GHSA-jjmv-6fv4-85vf
CVE: CVE-2019-10413
CWE: CWE-522
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-jjmv-6fv4-85vf
Type: github-advisory

## Affected
- Maven: `com.datatheorem.mobileappsecurity.jenkins.plugin:datatheorem-mobile-app-security` — affected >=0 <1.4.0

## Details
Data Theorem Mobile Security: CI/CD Plugin stored a proxy password unencrypted in job `config.xml` files on the Jenkins controller. This password could be viewed by users with Extended Read permission, or access to the Jenkins controller file system.

Data Theorem Mobile Security: CI/CD Plugin now stores the proxy password encrypted. Existing jobs need to have their configuration saved for existing plain text proxy passwords to be overwritten.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10413
- https://jenkins.io/security/advisory/2019-09-25/#SECURITY-1557
- http://www.openwall.com/lists/oss-security/2019/09/25/3
