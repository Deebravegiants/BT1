# [H] MongoDB Server may crash when inserting large documents

## Summary
Severity: High
Advisory: BIT-mongodb-2026-1847
Aliases: CVE-2026-1847
Ecosystem: Bitnami
Published: 2026-02-26
Source: https://osv.dev/vulnerability/BIT-mongodb-2026-1847
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=8.2.0 <8.2.4

## Details
Inserting certain large documents into a replica set could lead to replica set secondaries not being able to fetch the oplog from the primary. This could stall replication inside the replica set leading to server crash.

## References
- https://jira.mongodb.org/browse/SERVER-113532
- https://nvd.nist.gov/vuln/detail/CVE-2026-1847
