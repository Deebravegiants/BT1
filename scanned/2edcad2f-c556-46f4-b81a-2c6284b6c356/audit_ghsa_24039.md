# [M] SSRF vulnerability due to missing permission check in Jenkins JMS Messaging Plugin

## Summary
Severity: Medium
Advisory: GHSA-g3gj-632x-fhrh
CVE: CVE-2019-1003028
CWE: CWE-918
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-g3gj-632x-fhrh
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:jms-messaging` — affected >=0 <1.1.2

## Details
A server-side request forgery vulnerability exists in Jenkins JMS Messaging Plugin 1.1.1 and earlier in SSLCertificateAuthenticationMethod.java, UsernameAuthenticationMethod.java that allows attackers with Overall/Read permission to have Jenkins connect to a JMS endpoint.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-1003028
- https://jenkins.io/security/advisory/2019-02-19/#SECURITY-1033
- http://www.securityfocus.com/bid/107295
