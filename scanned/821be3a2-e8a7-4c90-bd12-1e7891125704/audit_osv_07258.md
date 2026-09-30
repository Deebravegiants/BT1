# [H] BIT-pgbouncer-2021-3935

## Summary
Severity: High
Advisory: BIT-pgbouncer-2021-3935
Aliases: CVE-2021-3935
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-pgbouncer-2021-3935
Type: osv

## Affected
- Bitnami: `pgbouncer` — affected >=0 <1.16.1

## Details
When PgBouncer is configured to use "cert" authentication, a man-in-the-middle attacker can inject arbitrary SQL queries when a connection is first established, despite the use of TLS certificate verification and encryption. This flaw affects PgBouncer versions prior to 1.16.1.

## References
- http://www.pgbouncer.org/changelog.html#pgbouncer-116x
- https://bugzilla.redhat.com/show_bug.cgi?id=2021251
- https://lists.debian.org/debian-lts-announce/2022/02/msg00016.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TNPCV3KRDI5PLLLKADFVIOHACQJLZMLI/
- https://nvd.nist.gov/vuln/detail/CVE-2021-3935
- https://lists.debian.org/debian-lts-announce/2025/05/msg00032.html
