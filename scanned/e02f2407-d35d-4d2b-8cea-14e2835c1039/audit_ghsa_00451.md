# [H] Improper Limitation of a Pathname ('Path Traversal') in org.apache.solr:solr-core

## Summary
Severity: High
Advisory: GHSA-387v-84cv-9qmc
CVE: CVE-2017-3163
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2018-10-18
Source: https://github.com/advisories/GHSA-387v-84cv-9qmc
Type: github-advisory

## Affected
- Maven: `org.apache.solr:solr-core` — affected >=0 <5.5.4
- Maven: `org.apache.solr:solr-core` — affected >=6.0.0 <6.4.1

## Details
When using the Index Replication feature, Apache Solr nodes can pull index files from a master/leader node using an HTTP API which accepts a file name. However, Solr before 5.5.4 and 6.x before 6.4.1 did not validate the file name, hence it was possible to craft a special request involving path traversal, leaving any file readable to the Solr server process exposed. Solr servers protected and restricted by firewall rules and/or authentication would not be at risk since only trusted clients and users would gain direct HTTP access.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-3163
- https://access.redhat.com/errata/RHSA-2018:1447
- https://access.redhat.com/errata/RHSA-2018:1448
- https://access.redhat.com/errata/RHSA-2018:1449
- https://access.redhat.com/errata/RHSA-2018:1450
- https://access.redhat.com/errata/RHSA-2018:1451
- https://github.com/advisories/GHSA-387v-84cv-9qmc
- https://lists.apache.org/thread.html/a6a33a186f293f9f9aecf3bd39c76252bfc49a79de4321dd2a53b488@%3Csolr-user.lucene.apache.org%3E
- https://www.debian.org/security/2018/dsa-4124
