# [H] Apache Solr has hardcoded credentials in the Basic Authentication setup tool

## Summary
Severity: High
Advisory: GHSA-qhr7-h655-pw6r
CVE: CVE-2026-44825
CWE: CWE-798
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-01
Source: https://github.com/advisories/GHSA-qhr7-h655-pw6r
Type: github-advisory

## Affected
- Maven: `org.apache.solr:solr-core` — affected >=9.4.0
- Maven: `org.apache.solr:solr-core` — affected 10.0.0

## Details
Hardcoded credentials in the Basic Authentication setup tool (bin/solr auth enable) in Apache Solr versions 9.4.0 through 9.10.1 and 10.0.0 allows a remote attacker to gain full administrative access to the cluster via publicly known default credentials installed silently alongside the user-specified account. 

As an immediate workaround without upgrading, delete the template users (superadmin, admin, search, index) from security.json or change their passwords.
The future, not yet released, versions 9.11.0 and 10.1.0 will not be vulnerable, and it will be enough to upgrade to solve the issue.

Not affected:
  *  Clusters where bin/solr auth enable was not used to bootstrap BasicAuth
  *  Clusters where template users have been assigned strong passwords after bootstrap

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-44825
- https://github.com/apache/lucene-solr
- https://lists.apache.org/thread/5xg6xr99glocp3zsg9ht2zlbwlrst7ch
- http://www.openwall.com/lists/oss-security/2026/05/29/6
