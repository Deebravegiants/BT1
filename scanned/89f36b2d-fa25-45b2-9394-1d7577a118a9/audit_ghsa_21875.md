# [M] DoS vulnerability in bundled XStream library in Jenkins Core

## Summary
Severity: Medium
Advisory: GHSA-34wx-x2w9-vqm3
CVE: CVE-2022-0538
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-02-10
Source: https://github.com/advisories/GHSA-34wx-x2w9-vqm3
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.320 <2.334
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <2.319.3

## Details
Jenkins 2.333 and earlier, LTS 2.319.2 and earlier is affected by the XStream library’s vulnerability [CVE-2021-43859](https://x-stream.github.io/CVE-2021-43859.html). This library is used by Jenkins to serialize and deserialize various XML files, like global and job `config.xml`, `build.xml`, and numerous others.

This allows attackers able to submit crafted XML files to Jenkins to be parsed as configuration, e.g. through the `POST config.xml` API, to cause a denial of service (DoS).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-0538
- https://github.com/jenkinsci/jenkins/commit/8276aef4cc3dd81810fe6bdf6fa48141632c4636
- https://www.jenkins.io/security/advisory/2022-02-09/#SECURITY-2602
- http://www.openwall.com/lists/oss-security/2022/02/09/1
