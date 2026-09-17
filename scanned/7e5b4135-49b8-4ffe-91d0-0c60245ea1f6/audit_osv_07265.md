# [C] BIT-pgpool-2025-22248

## Summary
Severity: Critical
Advisory: BIT-pgpool-2025-22248
Aliases: CVE-2025-22248, GHSA-mx38-x658-5fwj
Ecosystem: Bitnami
Published: 2025-05-13
Source: https://osv.dev/vulnerability/BIT-pgpool-2025-22248
Type: osv

## Affected
- Bitnami: `pgpool` — affected >=0 <4.6.0-1

## Details
The PgPool II component into a Bitnami Pgpool II container image comes by default configured with an 'repmgr' user that allows unauthenticated access to the database inside the cluster. This can be addressed by mounting and overwriting the Pgpool configuration file directly. If PgPool is exposed externally, a potential attacker could use this user to get access to the service.

## References
- https://github.com/bitnami/charts/security/advisories/GHSA-mx38-x658-5fwj
