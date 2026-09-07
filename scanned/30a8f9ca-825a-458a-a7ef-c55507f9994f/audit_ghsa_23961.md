# [M] XSS vulnerability in Jenkins Gatling Plugin

## Summary
Severity: Medium
Advisory: GHSA-hv53-qjg6-5pm9
CVE: CVE-2020-2173
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-hv53-qjg6-5pm9
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:gatling` — affected >=0 <1.3.0

## Details
Gatling Plugin 1.2.7 and earlier serves Gatling reports in a manner that bypasses the `Content-Security-Policy` protection introduced in Jenkins 1.641 and 1.625.3. This results in a cross-site scripting (XSS) vulnerability exploitable by users able to change report content.

Gatling Plugin 1.3.0 no longer allows viewing Gatling reports directly in Jenkins. Instead users need to download an archive containing the report.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2173
- https://github.com/jenkinsci/gatling-plugin/commit/8a9ae59c6b3328776d38af6596b35cef1ced05a7
- https://jenkins.io/security/advisory/2020-04-07/#SECURITY-1633
- http://www.openwall.com/lists/oss-security/2020/04/07/3
- ttps://github.com/jenkinsci/gatling-plugin
