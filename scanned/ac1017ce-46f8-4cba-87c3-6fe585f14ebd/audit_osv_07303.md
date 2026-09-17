# [M] BIT-postgresql-2020-21469

## Summary
Severity: Medium
Advisory: BIT-postgresql-2020-21469
Aliases: CVE-2020-21469
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-postgresql-2020-21469
Type: osv

## Affected
- Bitnami: `postgresql` — affected >=12.2.0 <12.2.1

## Details
An issue was discovered in PostgreSQL 12.2 allows attackers to cause a denial of service via repeatedly sending SIGHUP signals. NOTE: this is disputed by the vendor because untrusted users cannot send SIGHUP signals; they can only be sent by a PostgreSQL superuser, a user with pg_reload_conf access, or a user with sufficient privileges at the OS level (the postgres account or the root account).

## References
- https://www.postgresql.org/message-id/CAA8ZSMqAHDCgo07hqKoM5XJaoQy6Vv76O7966agez4ffyQktkA%40mail.gmail.com
- https://www.postgresql.org/message-id/flat/CAA8ZSMqAHDCgo07hqKoM5XJaoQy6Vv76O7966agez4ffyQktkA%40mail.gmail.com
- https://www.postgresql.org/support/security/
- https://nvd.nist.gov/vuln/detail/CVE-2020-21469
