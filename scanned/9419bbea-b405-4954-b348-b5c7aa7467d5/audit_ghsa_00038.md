# [H] Path Traversal in Hadoop

## Summary
Severity: High
Advisory: GHSA-6x48-j4x4-cqw3
CVE: CVE-2018-8009
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-12-21
Source: https://github.com/advisories/GHSA-6x48-j4x4-cqw3
Type: github-advisory

## Affected
- Maven: `org.apache.hadoop:hadoop-main` — affected >=3.1.0 <3.1.1
- Maven: `org.apache.hadoop:hadoop-main` — affected >=3.0.0 <3.0.3
- Maven: `org.apache.hadoop:hadoop-main` — affected >=2.9.0 <2.9.2
- Maven: `org.apache.hadoop:hadoop-main` — affected >=2.8.0 <2.8.5
- Maven: `org.apache.hadoop:hadoop-main` — affected >=0 <2.7.7

## Details
Apache Hadoop 3.1.0, 3.0.0-alpha to 3.0.2, 2.9.0 to 2.9.1, 2.8.0 to 2.8.4, 2.0.0-alpha to 2.7.6, 0.23.0 to 0.23.11 is exploitable via the zip slip vulnerability in places that accept a zip file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-8009
- https://github.com/apache/hadoop/commit/12258c7cff8d32710fbd8b9088a930e3ce27432
- https://github.com/apache/hadoop/commit/45a1c680c276c4501402f7bc4cebcf85a6fbc7f
- https://github.com/apache/hadoop/commit/65e55097da2bb3f2fbdf9ba1946da25fe58bec9
- https://github.com/apache/hadoop/commit/6a4ae6f6eeed1392a4828a5721fa1499f65bdde
- https://github.com/apache/hadoop/commit/fc4c20fc3469674cb584a4fb98bac7e3c2277c9
- https://access.redhat.com/errata/RHSA-2019:3892
- https://github.com/advisories/GHSA-6x48-j4x4-cqw3
- https://github.com/apache/hadoop
- https://hadoop.apache.org/cve_list.html#cve-2018-8009-http-cve-mitre-org-cgi-bin-cvename-cgi-name-cve-2018-8009-zip-slip-impact-on-apache-hadoop
- https://lists.apache.org/thread.html/708d94141126eac03011144a971a6411fcac16d9c248d1d535a39451@%3Csolr-user.lucene.apache.org%3E
- https://lists.apache.org/thread.html/a1c227745ce30acbcf388c5b0cc8423e8bf495d619cd0fa973f7f38d@%3Cuser.hadoop.apache.org%3E
- https://lists.apache.org/thread.html/r4dddf1705dbedfa94392913b2dad1cd2d1d89040facd389eea0b3510@%3Ccommits.druid.apache.org%3E
- https://lists.apache.org/thread.html/rb21df54a4e39732ce653d2aa5672e36a792b59eb6717f2a06bb8d02a@%3Ccommits.druid.apache.org%3E
- https://snyk.io/research/zip-slip-vulnerability
- http://www.securityfocus.com/bid/105927
