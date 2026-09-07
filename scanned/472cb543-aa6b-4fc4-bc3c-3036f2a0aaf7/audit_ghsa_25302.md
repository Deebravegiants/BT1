# [M] MitM on Jenkins Maven Plugin

## Summary
Severity: Medium
Advisory: GHSA-qhxw-54m9-6wwc
CVE: CVE-2017-1000397
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-qhxw-54m9-6wwc
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:maven-plugin` — affected >=0 <3.0

## Details
Jenkins Maven Plugin 2.17 and earlier bundled a version of the commons-httpclient library with the vulnerability CVE-2012-6153 that incorrectly verified SSL certificates, making it susceptible to man-in-the-middle attacks. Maven Plugin 3.0 no longer has a dependency on commons-httpclient.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000397
- https://www.jenkins.io/security/advisory/2017-10-11
