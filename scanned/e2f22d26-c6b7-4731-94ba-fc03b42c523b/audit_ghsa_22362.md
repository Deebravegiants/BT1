# [M] Jenkins Subversion Plugin Incorrect Authorization vulnerability

## Summary
Severity: Medium
Advisory: GHSA-w9gq-8q35-3jcc
CVE: CVE-2018-1000111
CWE: CWE-863
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-w9gq-8q35-3jcc
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:subversion` — affected >=0 <2.10.3

## Details
An improper authorization vulnerability exists in Jenkins Subversion Plugin version 2.10.2 and earlier in `SubversionStatus.java` and `SubversionRepositoryStatus.java` that allows an attacker with network access to obtain a list of nodes and users. As of version 2.10.3, the class handling requests to /subversion/ no longer extends the class handling requests to the …/search/ sub-path, therefore any such requests will fail.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000111
- https://github.com/jenkinsci/subversion-plugin/commit/25f6afbb02a5863f363b0a2f664ac717ace743b4
- https://github.com/jenkinsci/subversion-plugin
- https://jenkins.io/security/advisory/2018-02-26/#SECURITY-724
