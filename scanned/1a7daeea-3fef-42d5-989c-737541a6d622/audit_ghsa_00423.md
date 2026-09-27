# [C] Remote code execution occurs in Apache Solr

## Summary
Severity: Critical
Advisory: GHSA-mh7g-99w9-xpjm
CVE: CVE-2017-12629
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-10-17
Source: https://github.com/advisories/GHSA-mh7g-99w9-xpjm
Type: github-advisory

## Affected
- Maven: `org.apache.solr:solr-core` — affected >=7.0.0 <7.1.0
- Maven: `org.apache.solr:solr-core` — affected >=6.0.0 <6.6.2
- Maven: `org.apache.solr:solr-core` — affected >=5.5.0 <5.5.5

## Details
Remote code execution occurs in Apache Solr before versions 5.5.5, 6.6.2 and 7.1.0 by exploiting XXE in conjunction with use of a Config API add-listener command to reach the RunExecutableListener class. Elasticsearch, although it uses Lucene, is NOT vulnerable to this. Note that the XML external entity expansion vulnerability occurs in the XML Query Parser which is available, by default, for any query request with parameters deftype=xmlparser and can be exploited to upload malicious data to the /upload request handler or as Blind XXE using ftp wrapper in order to read arbitrary local files from the Solr server. Note also that the second vulnerability relates to remote code execution using the RunExecutableListener available on all affected versions of Solr

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-12629
- https://github.com/apache/lucene-solr/commit/3bba91131b5257e64b9d0a2193e1e32a145b2a2
- https://github.com/apache/lucene-solr/commit/d8000beebfb13ba0b6e754f84c760e11592d8d1
- https://github.com/apache/lucene-solr/commit/f9fd6e9e26224f26f1542224ce187e04c27b268
- https://www.exploit-db.com/exploits/43009
- https://www.debian.org/security/2018/dsa-4124
- https://usn.ubuntu.com/4259-1
- https://twitter.com/searchtools_avi/status/918904813613543424
- https://twitter.com/joshbressers/status/919258716297420802
- https://twitter.com/ApacheSolr/status/918731485611401216
- https://s.apache.org/FJDl
- https://lists.debian.org/debian-lts-announce/2018/01/msg00028.html
- https://lists.apache.org/thread.html/r95df34bb158375948da82b4dfe9a1b5d528572d586584162f8f5aeef@%3Cusers.solr.apache.org%3E
- https://lists.apache.org/thread.html/r3da74965aba2b5f5744b7289ad447306eeb2940c872801819faa9314@%3Cusers.solr.apache.org%3E
- https://lists.apache.org/thread.html/r26c996b068ef6c5e89aa59acb769025cfd343a08e63fbe9e7f3f720f@%3Coak-issues.jackrabbit.apache.org%3E
- https://lists.apache.org/thread.html/r140128dc6bb4f4e0b6a39e962c7ca25a8cbc8e48ed766176c931fccc@%3Cusers.solr.apache.org%3E
- https://issues.apache.org/jira/browse/SOLR-11477
- https://github.com/apache/lucene
- https://github.com/advisories/GHSA-mh7g-99w9-xpjm
- https://access.redhat.com/errata/RHSA-2018:0005
