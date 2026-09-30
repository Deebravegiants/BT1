# [H] CSRF vulnerability in Jenkins CloudBees AWS Credentials Plugin

## Summary
Severity: High
Advisory: GHSA-pv4m-7c68-f4c5
CVE: CVE-2022-27198
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-03-16
Source: https://github.com/advisories/GHSA-pv4m-7c68-f4c5
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:aws-credentials` — affected >=0

## Details
A cross-site request forgery (CSRF) vulnerability in Jenkins CloudBees AWS Credentials Plugin 189.v3551d5642995 and earlier allows attackers with Overall/Read permission to connect to an AWS service using an attacker-specified token.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-27198
- https://github.com/jenkinsci/aws-credentials-plugin/commit/cbf183ce58b955f17d93fdc1ac4d19a8ebe693db
- https://github.com/jenkinsci/aws-credentials-plugin
- https://www.jenkins.io/security/advisory/2022-03-15/#SECURITY-2351
- http://www.openwall.com/lists/oss-security/2022/03/15/2
