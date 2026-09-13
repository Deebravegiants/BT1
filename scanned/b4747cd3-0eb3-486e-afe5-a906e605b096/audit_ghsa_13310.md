# [M] Jenkins External Monitor Job Type Plugin XML external entity vulnerability

## Summary
Severity: Medium
Advisory: GHSA-g4c3-4f3v-84x8
CVE: CVE-2023-37942
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2023-07-12
Source: https://github.com/advisories/GHSA-g4c3-4f3v-84x8
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:external-monitor-job` — affected >=0 <207.v98a

## Details
Jenkins External Monitor Job Type Plugin 206.v9a_94ff0b_4a_10 and earlier does not configure its XML parser to prevent XML external entity (XXE) attacks.

This allows attackers with Item/Build permission to have Jenkins parse a crafted HTTP request with XML data that uses external entities for extraction of secrets from the Jenkins controller or server-side request forgery.

External Monitor Job Type Plugin 207.v98a_a_37a_85525 disables external entity resolution for its XML parser.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-37942
- https://www.jenkins.io/security/advisory/2023-07-12/#SECURITY-3133
- http://www.openwall.com/lists/oss-security/2023/07/12/2
