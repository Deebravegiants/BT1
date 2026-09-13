# [M] Insertion of Sensitive Information into Externally-Accessible File or Directory in Jenkins Credentials Plugin

## Summary
Severity: Medium
Advisory: GHSA-xm94-9jw8-p6hw
CVE: CVE-2019-10320
CWE: CWE-200, CWE-538
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-xm94-9jw8-p6hw
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:credentials` — affected >=0 <2.1.19

## Details
Jenkins Credentials Plugin 2.1.18 and earlier allowed users with permission to create or update credentials to confirm the existence of files on the Jenkins master with an attacker-specified path, and obtain the certificate content of files containing a PKCS#12 certificate.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10320
- https://github.com/jenkinsci/credentials-plugin/commit/40d0b5cc53c265b601ffaa4469310fad390a80fb
- https://access.redhat.com/errata/RHBA-2019:1605
- https://access.redhat.com/errata/RHSA-2019:1636
- https://jenkins.io/security/advisory/2019-05-21/#SECURITY-1322
- https://wwws.nightwatchcybersecurity.com/2019/05/23/exploring-the-file-system-via-jenkins-credentials-plugin-vulnerability-cve-2019-10320
- http://seclists.org/fulldisclosure/2019/May/39
- http://www.openwall.com/lists/oss-security/2019/05/21/1
- http://www.securityfocus.com/bid/108462
