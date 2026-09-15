# [M] URLTrigger Plugin server-side request forgery vulnerability

## Summary
Severity: Medium
Advisory: GHSA-rv87-vcv4-fjvr
CVE: CVE-2018-1000606
CWE: CWE-918
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-rv87-vcv4-fjvr
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:urltrigger` — affected >=0 <0.43

## Details
A server-side request forgery vulnerability exists in Jenkins URLTrigger Plugin 0.41 and earlier in URLTrigger.java that allows attackers with Overall/Read access to cause Jenkins to send a GET request to a specified URL. As of version 0.43, this form validation method no longer connects to a user provided URL.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000606
- https://github.com/jenkinsci/urltrigger-plugin/commit/46220e69c220bacf8eb23911c8feba9dd68d1a26
- https://github.com/jenkinsci/urltrigger-plugin/commit/aec43e370550b26636aa9cab0f23a5cbcffdc44f
- https://github.com/jenkinsci/urltrigger-plugin
- https://jenkins.io/security/advisory/2018-06-25/#SECURITY-819
