# [M] BIT-guacamole-2021-41767

## Summary
Severity: Medium
Advisory: BIT-guacamole-2021-41767
Aliases: BIT-guacamole-server-2021-41767, CVE-2021-41767
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-guacamole-2021-41767
Type: osv

## Affected
- Bitnami: `guacamole` — affected >=0 <1.3.0

## Details
Apache Guacamole 1.3.0 and older may incorrectly include a private tunnel identifier in the non-private details of some REST responses. This may allow an authenticated user who already has permission to access a particular connection to read from or interact with another user's active use of that same connection.

## References
- http://www.openwall.com/lists/oss-security/2022/01/11/6
- https://lists.apache.org/thread/5l31k4jmzdsfz0xt8osrbl878gb3b7ro
