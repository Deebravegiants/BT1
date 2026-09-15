# [M] Jenkins Call Remote Job Plugin has Insufficiently Protected Credentials

## Summary
Severity: Medium
Advisory: GHSA-j8c7-fm85-6jj6
CVE: CVE-2019-10422
CWE: CWE-522
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-j8c7-fm85-6jj6
Type: github-advisory

## Affected
- Maven: `org.ukiuni.callOtherJenkins:call-remote-job-plugin` — affected >=0

## Details
Call Remote Job Plugin stores a password unencrypted in job `config.xml` files on the Jenkins controller. This password can be viewed by users with Extended Read permission, or access to the Jenkins controller file system.

As of publication of this advisory, there is no fix.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10422
- https://jenkins.io/security/advisory/2019-09-25/#SECURITY-1548
- http://www.openwall.com/lists/oss-security/2019/09/25/3
