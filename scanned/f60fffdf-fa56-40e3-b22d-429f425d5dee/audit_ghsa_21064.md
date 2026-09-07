# [M] Lucene-Search Plugin does not perform permission checks in several HTTP endpoints

## Summary
Severity: Medium
Advisory: GHSA-m8w5-vwq3-gp8f
CVE: CVE-2022-36910
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-07-28
Source: https://github.com/advisories/GHSA-m8w5-vwq3-gp8f
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:lucene-search` — affected >=0 <387.v938a

## Details
Jenkins Lucene-Search Plugin 370.v62a5f618cd3a and earlier does not perform permission checks in several HTTP endpoints.

This allows attackers with Overall/Read permission to reindex the database and to obtain information about jobs otherwise inaccessible to them.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-36910
- https://github.com/jenkinsci/lucene-search-plugin/commit/b56e0aba81a355356d20824e81038e9720bc7e2e
- https://www.jenkins.io/security/advisory/2022-07-27/#SECURITY-2048
- http://www.openwall.com/lists/oss-security/2022/07/27/1
