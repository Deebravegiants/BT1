# [H] BIT-timescaledb-2023-25149

## Summary
Severity: High
Advisory: BIT-timescaledb-2023-25149
Aliases: CVE-2023-25149, GHSA-44jh-j22r-33wq
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-timescaledb-2023-25149
Type: osv

## Affected
- Bitnami: `timescaledb` — affected >=2.8.0 <2.9.2

## Details
TimescaleDB, an open-source time-series SQL database, has a privilege escalation vulnerability in versions 2.8.0 through 2.9.2. During installation, TimescaleDB creates a telemetry job that is runs as the installation user. The queries run as part of the telemetry data collection were not run with a locked down `search_path`, allowing malicious users to create functions that would be executed by the telemetry job, leading to privilege escalation. In order to be able to take advantage of this vulnerability, a user would need to be able to create objects in a database and then get a superuser to install TimescaleDB into their database. When TimescaleDB is installed as trusted extension, non-superusers can install the extension without help from a superuser.Version 2.9.3 fixes this issue. As a mitigation, the `search_path` of the user running the telemetry job can be locked down to not include schemas writable by other users. The vulnerability is not exploitable on instances in Timescale Cloud and Managed Service for TimescaleDB due to additional security provisions in place on those platforms.

## References
- https://github.com/timescale/timescaledb/pull/5259
- https://github.com/timescale/timescaledb/releases/tag/2.9.3
- https://github.com/timescale/timescaledb/security/advisories/GHSA-44jh-j22r-33wq
