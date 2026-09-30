# [M] Jenkins Kanboard Plugin vulnerable to Server-side request forgery (SSRF)

## Summary
Severity: Medium
Advisory: GHSA-278v-j3cr-jv2x
CVE: CVE-2019-1003020
CWE: CWE-918
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-278v-j3cr-jv2x
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:kanboard` — affected >=0 <1.5.11

## Details
A server-side request forgery vulnerability exists in Jenkins Kanboard Plugin 1.5.10 and earlier in KanboardGlobalConfiguration.java that allows attackers with Overall/Read permission to submit a GET request to an attacker-specified URL.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-1003020
- https://jenkins.io/security/advisory/2019-01-28/#SECURITY-818
