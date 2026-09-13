# [M] Awaitable Hello Command in Exhaust Mode Unthrottled Response Loop Leading to Denial of Service

## Summary
Severity: Medium
Advisory: BIT-mongodb-2026-13074
Aliases: CVE-2026-13074
Ecosystem: Bitnami
Published: 2026-08-19
Source: https://osv.dev/vulnerability/BIT-mongodb-2026-13074
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=8.3.0 <8.3.7

## Details
An unauthenticated remote client can cause excessive CPU consumption on a MongoDB server by sending a specific combination of parameters to the awaitable hello command in exhaust mode. The server's handling of this combination results in a response loop that bypasses normal throttling, allowing a small number of connections to degrade server availability.

## References
- https://jira.mongodb.org/browse/SERVER-128517
- https://nvd.nist.gov/vuln/detail/CVE-2026-13074
