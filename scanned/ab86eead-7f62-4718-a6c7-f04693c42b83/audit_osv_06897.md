# [H] Incorrect Handling of incomplete data may prevent mongoS from Accepting New Connections

## Summary
Severity: High
Advisory: BIT-mongodb-2025-6714
Aliases: CVE-2025-6714
Ecosystem: Bitnami
Published: 2025-10-05
Source: https://osv.dev/vulnerability/BIT-mongodb-2025-6714
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=8.0.0 <8.0.9

## Details
MongoDB Server's mongos component can become unresponsive to new connections due to incorrect handling of incomplete data. This affects MongoDB when configured with load balancer support. This issue affects MongoDB Server v6.0 prior to 6.0.23, MongoDB Server v7.0 prior to 7.0.20 and MongoDB Server v8.0 prior to 8.0.9

Required Configuration:

This affects MongoDB sharded clusters when configured with load balancer support for mongos using HAProxy on specified ports.

## References
- https://jira.mongodb.org/browse/SERVER-106753
- https://nvd.nist.gov/vuln/detail/CVE-2025-6714
