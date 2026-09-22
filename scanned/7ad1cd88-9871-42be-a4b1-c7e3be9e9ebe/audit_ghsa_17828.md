# [M] Apache Solr Relative Path Traversal vulnerability

## Summary
Severity: Medium
Advisory: GHSA-4p5m-gvpf-f3x5
CVE: CVE-2024-52012
CWE: CWE-23
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2025-01-27
Source: https://github.com/advisories/GHSA-4p5m-gvpf-f3x5
Type: github-advisory

## Affected
- Maven: `org.apache.solr:solr-core` — affected >=6.6 <9.8.0

## Details
Relative Path Traversal vulnerability in Apache Solr.

Solr instances running on Windows are vulnerable to arbitrary filepath write-access, due to a lack of input-sanitation in the "configset upload" API.  Commonly known as a "zipslip", maliciously constructed ZIP files can use relative filepaths to write data to unanticipated parts of the filesystem.  
This issue affects Apache Solr: from 6.6 through 9.7.0.

Users are recommended to upgrade to version 9.8.0, which fixes the issue.  Users unable to upgrade may also safely prevent the issue by using Solr's "Rule-Based Authentication Plugin" to restrict access to the configset upload API, so that it can only be accessed by a trusted set of administrators/users.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-52012
- https://github.com/apache/solr/commit/5795edd143b8fcb2ffaf7f278a099b8678adf396
- https://github.com/apache/solr
- https://issues.apache.org/jira/browse/SOLR-17543
- https://lists.apache.org/thread/yp39pgbv4vf1746pf5yblz84lv30vfxd
- http://www.openwall.com/lists/oss-security/2025/01/26/2
