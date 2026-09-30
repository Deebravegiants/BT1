# [M] Apache Solr's Streaming Expressions allow users to extract data from other Solr Clouds

## Summary
Severity: Medium
Advisory: GHSA-xrj7-x7gp-wwqr
CVE: CVE-2023-50298
CWE: CWE-200, CWE-922
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-02-09
Source: https://github.com/advisories/GHSA-xrj7-x7gp-wwqr
Type: github-advisory

## Affected
- Maven: `org.apache.solr:solr-solrj-streaming` — affected >=9.0.0 <9.4.1
- Maven: `org.apache.solr:solr-solrj-streaming` — affected >=6.0.0 <8.11.3
- Maven: `org.apache.solr:solr-solrj` — affected >=9.0.0 <9.4.1
- Maven: `org.apache.solr:solr-solrj` — affected >=6.0.0 <8.11.3

## Details
Exposure of Sensitive Information to an Unauthorized Actor vulnerability in Apache Solr. This issue affects Apache Solr from 6.0.0 through 8.11.2, from 9.0.0 before 9.4.1.

Solr Streaming Expressions allows users to extract data from other Solr Clouds, using a "zkHost" parameter.

When original SolrCloud is setup to use ZooKeeper credentials and ACLs, they will be sent to whatever "zkHost" the user provides.

An attacker could setup a server to mock ZooKeeper, that accepts ZooKeeper requests with credentials and ACLs and extracts the sensitive information, then send a streaming expression using the mock server's address in "zkHost".

Streaming Expressions are exposed via the "/streaming" handler, with "read" permissions.

Users are recommended to upgrade to version 8.11.3 or 9.4.1, which fix the issue.

From these versions on, only zkHost values that have the same server address (regardless of chroot), will use the given ZooKeeper credentials and ACLs when connecting.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-50298
- https://github.com/apache/lucene-solr/commit/61c956c426b2cfb85ccef55d1afca4335eacd269
- https://github.com/apache/solr/commit/e2bf1f434aad873fbb24c21d46ac00e888806d98
- https://github.com/apache/solr
- https://issues.apache.org/jira/browse/SOLR-17098
- https://solr.apache.org/security.html#cve-2023-50298-apache-solr-can-expose-zookeeper-credentials-via-streaming-expressions
- http://www.openwall.com/lists/oss-security/2024/02/09/2
- http://www.openwall.com/lists/oss-security/2024/02/09/3
