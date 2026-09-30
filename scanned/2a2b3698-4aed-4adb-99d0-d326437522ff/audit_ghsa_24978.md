# [M] Jenkins Perforce Plugin uses ineffective credentials encryption

## Summary
Severity: Medium
Advisory: GHSA-cwxx-gwwj-pqjq
CVE: CVE-2018-1000145
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-cwxx-gwwj-pqjq
Type: github-advisory

## Affected
- Maven: `org.jvnet.hudson.plugins:perforce` — affected >=0

## Details
An exposure of sensitive information vulnerability exists in Jenkins Perforce Plugin version 1.3.36 and older in PerforcePasswordEncryptor.java that allows attackers with local file system access to obtain encrypted Perforce passwords and decrypt them.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000145
- https://github.com/jenkinsci/perforce-plugin
- https://jenkins.io/security/advisory/2018-03-26/#SECURITY-373
