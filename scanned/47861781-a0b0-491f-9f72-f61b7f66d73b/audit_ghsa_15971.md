# [H] Insecure Default Initialization of Resource vulnerability in Apache Solr

## Summary
Severity: High
Advisory: GHSA-h7w9-c5vx-x7j3
CVE: CVE-2024-45217
CWE: CWE-1188
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-10-16
Source: https://github.com/advisories/GHSA-h7w9-c5vx-x7j3
Type: github-advisory

## Affected
- Maven: `org.apache.solr:solr` — affected >=6.6.0 <8.11.4
- Maven: `org.apache.solr:solr` — affected >=9.0.0 <9.7.0

## Details
New ConfigSets that are created via a Restore command, which copy a configSet from the backup and give it a new name, are created without setting the "trusted" metadata.
ConfigSets that do not contain the flag are trusted implicitly if the metadata is missing, therefore this leads to "trusted" ConfigSets that may not have been created with an Authenticated request.
"trusted" ConfigSets are able to load custom code into classloaders, therefore the flag is supposed to only be set when the request that uploads the ConfigSet is Authenticated & Authorized.

This issue affects Apache Solr: from 6.6.0 before 8.11.4, from 9.0.0 before 9.7.0. This issue does not affect Solr instances that are secured via Authentication/Authorization.

Users are primarily recommended to use Authentication and Authorization when running Solr. However, upgrading to version 9.7.0, or 8.11.4 will mitigate this issue otherwise.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-45217
- https://issues.apache.org/jira/browse/SOLR-17418
- https://solr.apache.org/security.html#cve-2024-45217-apache-solr-configsets-created-during-a-backup-restore-command-are-trusted-implicitly
- http://svn.apache.org/viewvc/lucene/dev/branches/branch_4x/solr/webapp
- http://www.openwall.com/lists/oss-security/2024/10/15/9
