# [M] Missing permission check in Jenkins Project Inheritance Plugin

## Summary
Severity: Medium
Advisory: GHSA-hj32-9mcw-5cwh
CVE: CVE-2020-2197
CWE: CWE-285
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-hj32-9mcw-5cwh
Type: github-advisory

## Affected
- Maven: `hudson.plugins:project-inheritance` — affected >=0

## Details
Jenkins limits access to job configuration XML data (`config.xml`) to users with Job/ExtendedRead permission, typically implied by Job/Configure permission. Project Inheritance Plugin has several job inspection features, including the API URL `/job/…​/getConfigAsXML` for its Inheritance Project job type that does something similar.

Project Inheritance Plugin 21.04.03 and earlier does not check permissions for this new endpoint, granting access to job configuration XML data to every user with Job/Read permission.

Additionally, the encrypted values of secrets stored in the job configuration are not redacted, as they would be by the `config.xml` API for users without Job/Configure permission.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2197
- https://github.com/github/advisory-database/pull/1356
- https://jenkins.io/security/advisory/2020-06-03/#SECURITY-1582
- http://www.openwall.com/lists/oss-security/2020/06/03/3
