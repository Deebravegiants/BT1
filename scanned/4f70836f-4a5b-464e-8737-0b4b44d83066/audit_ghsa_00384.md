# [H] Race condition in org.apache.hbase:hbase-thrift

## Summary
Severity: High
Advisory: GHSA-r86j-2gc6-2cq9
CVE: CVE-2018-8025
CWE: CWE-362
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-10-18
Source: https://github.com/advisories/GHSA-r86j-2gc6-2cq9
Type: github-advisory

## Affected
- Maven: `org.apache.hbase:hbase-thrift` — affected >=2.0.0 <2.0.1
- Maven: `org.apache.hbase:hbase-thrift` — affected >=1.4.0 <1.4.5
- Maven: `org.apache.hbase:hbase-thrift` — affected >=1.3.0 <1.3.2.1
- Maven: `org.apache.hbase:hbase-thrift` — affected >=0 <1.2.6.1

## Details
An issue in Apache HBase affects the optional "Thrift 1" API server when running over HTTP. There is a race-condition which could lead to authenticated sessions being incorrectly applied to users, e.g. one authenticated user would be considered a different user or an unauthenticated user would be treated as an authenticated user. https://issues.apache.org/jira/browse/HBASE-20664 implements a fix for this issue. It has been fixed in versions: 1.2.6.1, 1.3.2.1, 1.4.5, 2.0.1.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-8025
- https://github.com/apache/hbase/commit/0c42acbdf86d08af3003105a26a2201f75f2e2c
- https://github.com/apache/hbase/commit/30e98b4455f971c9cb3c02ac7b2daeebe4ee6f2
- https://github.com/apache/hbase/commit/625d4d002620139f49c8201f95b789b6a715cd4
- https://github.com/apache/hbase/commit/7fe07075b35a816725ba18f6dd43d3fa84e08f9
- https://github.com/apache/hbase/commit/bf25c1cb7221178388baaa58f0b16a408e151a6
- https://github.com/advisories/GHSA-r86j-2gc6-2cq9
- https://issues.apache.org/jira/browse/HBASE-20664
- https://lists.apache.org/thread.html/a919e38f587c714c386a01d40fc8f45bd4219a65aaf2dc0bb4eccc96@%3Cdev.hbase.apache.org%3E
- http://www.securityfocus.com/bid/104554
