# [M] Improper masking of credentials in Jenkins Pipeline Maven Integration Plugin

## Summary
Severity: Medium
Advisory: GHSA-9v8g-f9mq-739g
CVE: CVE-2023-41934
CWE: CWE-532
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-09-06
Source: https://github.com/advisories/GHSA-9v8g-f9mq-739g
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:pipeline-maven` — affected >=0 <1331.v003efa_fd6e81

## Details
Jenkins Pipeline Maven Integration Plugin 1330.v18e473854496 and earlier does not properly mask (i.e., replace with asterisks) usernames of credentials specified in custom Maven settings in Pipeline build logs if "Treat username as secret" is checked.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-41934
- https://www.jenkins.io/security/advisory/2023-09-06/#SECURITY-3257
- http://www.openwall.com/lists/oss-security/2023/09/06/9
