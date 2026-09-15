# [M] Password stored in plain text by ECX Copy Data Management Plugin

## Summary
Severity: Medium
Advisory: GHSA-6793-gmp9-2535
CVE: CVE-2020-2128
CWE: CWE-256, CWE-522
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-6793-gmp9-2535
Type: github-advisory

## Affected
- Maven: `com.catalogic.ecxjenkins:catalogic-ecx` — affected >=0

## Details
Jenkins ECX Copy Data Management Plugin 1.9 and earlier stores a password unencrypted in job config.xml files on the Jenkins master where it can be viewed by users with Extended Read permission, or access to the master file system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2128
- https://github.com/jenkinsci/catalogic-ecx-plugin
- https://jenkins.io/security/advisory/2020-02-12/#SECURITY-1549
- http://www.openwall.com/lists/oss-security/2020/02/12/3
