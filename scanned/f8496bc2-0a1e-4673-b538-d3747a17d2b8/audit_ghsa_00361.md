# [H] There is a XML external entity expansion (XXE) vulnerability in Apache Solr 

## Summary
Severity: High
Advisory: GHSA-3pph-2595-cgfh
CVE: CVE-2018-1308
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2018-10-17
Source: https://github.com/advisories/GHSA-3pph-2595-cgfh
Type: github-advisory

## Affected
- Maven: `org.apache.solr:solr-core` — affected >=1.2 <6.6.3
- Maven: `org.apache.solr:solr-core` — affected >=7.0.0 <7.3.0

## Details
This vulnerability in Apache Solr 1.2 to 6.6.2 and 7.0.0 to 7.2.1 relates to an XML external entity expansion (XXE) in the `&dataConfig=<inlinexml>` parameter of Solr's DataImportHandler. It can be used as XXE using file/ftp/http protocols in order to read arbitrary local files from the Solr server or the internal network.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1308
- https://github.com/apache/lucene-solr/commit/3530397f1777332872eac2760f9aa0e2ae1d7450
- https://github.com/apache/lucene-solr/commit/739a7933
- https://github.com/apache/lucene-solr/commit/dd3be31f7062dcb2f3b2d7f0e89df29e197dee63
- https://github.com/advisories/GHSA-3pph-2595-cgfh
- https://issues.apache.org/jira/browse/SOLR-11971
- https://lists.apache.org/thread.html/708d94141126eac03011144a971a6411fcac16d9c248d1d535a39451@%3Csolr-user.lucene.apache.org%3E
- https://lists.debian.org/debian-lts-announce/2018/04/msg00025.html
- https://mail-archives.apache.org/mod_mbox/www-announce/201804.mbox/%3C000001d3cf68%245ac69af0%241053d0d0%24%40apache.org%3E
- https://www.debian.org/security/2018/dsa-4194
