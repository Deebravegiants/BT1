# [M] CSRF vulnerability in Jenkins Google Cloud Backup Plugin

## Summary
Severity: Medium
Advisory: GHSA-m485-79jq-cxx7
CVE: CVE-2022-36916
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-07-28
Source: https://github.com/advisories/GHSA-m485-79jq-cxx7
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:google-cloud-backup` — affected >=0

## Details
A cross-site request forgery (CSRF) vulnerability in Jenkins Google Cloud Backup Plugin 0.6 and earlier does not perform a permission check in an HTTP endpoint.

Additionally, this HTTP endpoint does not require POST requests, resulting in a cross-site request forgery (CSRF) vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-36916
- https://github.com/jenkinsci/google-cloud-backup-plugin
- https://www.jenkins.io/security/advisory/2022-07-27/#SECURITY-2656
- http://www.openwall.com/lists/oss-security/2022/07/27/1
