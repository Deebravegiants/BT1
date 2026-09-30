# [M] Jenkins Copy To Slave Plugin allows access to arbitrary files on the Jenkins controller file system 

## Summary
Severity: Medium
Advisory: GHSA-9jrh-hch8-rr5c
CVE: CVE-2018-1000148
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-9jrh-hch8-rr5c
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:copy-to-slave` — affected >=0

## Details
An exposure of sensitive information vulnerability exists in Jenkins Copy To Slave Plugin version 1.4.4 and older in CopyToSlaveBuildWrapper.java that allows attackers with permission to configure jobs to read arbitrary files from the Jenkins master file system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000148
- https://jenkins.io/security/advisory/2018-03-26/#SECURITY-545
