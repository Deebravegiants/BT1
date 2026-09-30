# [M] Arbitrary file write vulnerability in Jenkins Fortify CloudScan Plugin

## Summary
Severity: Medium
Advisory: GHSA-8864-pwhg-3mp2
CVE: CVE-2018-1000607
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-8864-pwhg-3mp2
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:fortify-cloudscan-jenkins-plugin` — affected >=0 <1.5.2

## Details
A arbitrary file write vulnerability exists in Jenkins Fortify CloudScan Plugin 1.5.1 and earlier in ArchiveUtil.java that allows attackers able to control rulepack zip file contents to overwrite any file on the Jenkins master file system, only limited by the permissions of the user the Jenkins master process is running as.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000607
- https://jenkins.io/security/advisory/2018-06-25/#SECURITY-870
