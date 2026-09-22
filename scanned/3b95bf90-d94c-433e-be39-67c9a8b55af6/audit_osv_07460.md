# [H] Privilege escalation from having CREATE access on a keyspace in Scylladb

## Summary
Severity: High
Advisory: BIT-scylladb-2023-33972
Aliases: CVE-2023-33972, GHSA-ww5v-p45p-3vhq
Ecosystem: Bitnami
Published: 2024-05-14
Source: https://osv.dev/vulnerability/BIT-scylladb-2023-33972
Type: osv

## Affected
- Bitnami: `scylladb` — affected >=0 <5.2.9

## Details
Scylladb is a NoSQL data store using the seastar framework, compatible with Apache Cassandra. Authenticated users who are authorized to create tables in a keyspace can escalate their privileges to access a table in the same keyspace, even if they don't have permissions for that table. This issue has not yet been patched. A workaround to address this issue is to disable CREATE privileges on a keyspace, and create new tables on behalf of other users.

## References
- https://github.com/scylladb/scylladb/security/advisories/GHSA-ww5v-p45p-3vhq
- https://nvd.nist.gov/vuln/detail/CVE-2023-33972
