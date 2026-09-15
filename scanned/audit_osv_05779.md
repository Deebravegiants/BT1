# [M] BIT-guacamole-2020-11997

## Summary
Severity: Medium
Advisory: BIT-guacamole-2020-11997
Aliases: BIT-guacamole-server-2020-11997, CVE-2020-11997
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-guacamole-2020-11997
Type: osv

## Affected
- Bitnami: `guacamole` — affected >=0 <1.2.0

## Details
Apache Guacamole 1.2.0 and earlier do not consistently restrict access to connection history based on user visibility. If multiple users share access to the same connection, those users may be able to see which other users have accessed that connection, as well as the IP addresses from which that connection was accessed, even if those users do not otherwise have permission to see other users.

## References
- https://lists.apache.org/thread.html/r1a9ae9d1608c9f846875c4191cd738f95543d1be06b52dc1320e8117%40%3Cannounce.guacamole.apache.org%3E
