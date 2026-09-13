# [C] Default superuser cassandra:cassandra left active when CASSANDRA_USER is customized

## Summary
Severity: Critical
Advisory: BIT-cassandra-2026-47846
Aliases: CVE-2026-47846
Ecosystem: Bitnami
Published: 2026-06-18
Source: https://osv.dev/vulnerability/BIT-cassandra-2026-47846
Type: osv

## Affected
- Bitnami: `cassandra` — affected >=5.0.0 <5.0.8-0

## Details
Bitnami Cassandra container images are affected by a retained default superuser vulnerability. When a custom administrator account is configured via the CASSANDRA_USER environment variable, the container initialization script creates the new superuser account but fails to drop the built-in cassandra account in certain scenarios. This leaves the default cassandra:cassandra superuser active as an unintended access path. Any remote attacker who knows the default Cassandra credentials, can authenticate to the cluster as a full superuser regardless of the operator's configuration, bypassing the intent to replace the built-in account.

## References
- https://github.com/bitnami/containers/security/advisories/GHSA-8q3j-37vg-8fc2
