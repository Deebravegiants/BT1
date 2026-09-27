# [C] Apache Hive: SQL Injection vulnerability in HiveMetaStore partition-name direct-SQL paths

## Summary
Severity: Critical
Advisory: CVE-2026-49845
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/CVE-2026-49845
Type: osv

## Details
SQL injection in Hive Metastore direct SQL partition-name resolution in Apache Hive before 4.2.1 on all platforms allows authenticated users with access to Hive Metastore APIs to read, modify, or affect unintended partition metadata (including statistics updates, truncation targets, and file-metadata cache operations) via crafted partition names in metastore RPC requests when direct SQL is enabled (the default). Users are recommended to upgrade to version 4.2.1, which fixes this issue.

Details about the issue:
Several Hive Metastore RPCs resolve partitions by full partition name (PART_NAME) through direct-SQL helpers. In those paths, client-supplied partition names are embedded into SQL using string concatenation (DirectSqlUpdatePart.quoteString() → '...') instead of bind parameters. A partition name containing a single quote (and crafted SQL) can alter the generated WHERE clause so that lookups intended for one partition match additional rows. That can affect reads, stats updates, truncate targets, metadata-cache targets, and related operations when metastore.try.direct.sql is enabled (default: true). An authenticated or network-trusted caller with the ability to invoke Hive Metastore partition-name APIs against a target table (directly or via Hive/other clients), when direct SQL is enabled can perform this attack. Also, the impact is mainly within table & partition targeting (read/update/truncate/drop/cache the wrong partitions in a table they can reference), not arbitrary cross-database access via this bug alone.

## References
- https://repo.maven.apache.org/maven2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/49xxx/CVE-2026-49845.json
- https://lists.apache.org/thread/6d56mk501fp4f8cb5wvrpj2jwd9knt05
- https://nvd.nist.gov/vuln/detail/CVE-2026-49845
- https://issues.apache.org/jira/browse/HIVE-29622
- https://github.com/apache/hive/commit/ca64f08a8e43db9845b47d5fa2e96f7fdea7288e
- https://github.com/apache/hive
