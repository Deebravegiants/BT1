# [M] Default replication credential monitor:monitor created

## Summary
Severity: Medium
Advisory: BIT-mariadb-galera-2026-47847
Aliases: CVE-2026-47847
Ecosystem: Bitnami
Published: 2026-06-18
Source: https://osv.dev/vulnerability/BIT-mariadb-galera-2026-47847
Type: osv

## Affected
- Bitnami: `mariadb-galera` — affected >=12.3.0 <12.3.2-0

## Details
Bitnami MariaDB Galera container images and Helm chart are affected by a hardcoded default credential vulnerability in the Galera replication health-check user. The MARIADB_REPLICATION_USER and MARIADB_REPLICATION_PASSWORD environment variables defaulted to monitor and monitor respectively. This user is granted REPLICATION CLIENT privileges from any host ('%'). The Bitnami Helm chart for MariaDB Galera did not expose parameters to configure this user's credentials, resulting in all chart deployments using this publicly known credential by default. A remote attacker with network access to the MariaDB port can authenticate as monitor:monitor and query replication topology and status information.

## References
- https://github.com/bitnami/containers/security/advisories/GHSA-xcv9-cg8m-3mf2
