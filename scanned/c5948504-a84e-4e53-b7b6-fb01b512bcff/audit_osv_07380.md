# [C] ProxySQL: PROXY-Protocol-v1 UNKNOWN parses spoofed source IP, bypassing mysql_query_rules.client_addr ACL

## Summary
Severity: Critical
Advisory: BIT-proxysql-2026-48772
Aliases: CVE-2026-48772, GHSA-gw94-85m2-x8v2
Ecosystem: Bitnami
Published: 2026-08-17
Source: https://osv.dev/vulnerability/BIT-proxysql-2026-48772
Type: osv

## Affected
- Bitnami: `proxysql` — affected >=2.0.0 <3.0.9

## Details
ProxySQL is a proxy for MySQL and its forks, as well as PostgreSQL. In versions 2.0.0 through 3.0.8, the ProxySQL MySQL frontend accepts the `PROXY UNKNOWN <addr> <addr> <port> <port>\r\n` PP1 frame as a well-formed PROXY protocol header. The HAProxy PROXY protocol v1 specification says that when the protocol token is `UNKNOWN`, the receiver MUST ignore any address fields that follow it, because the proxy has declared it cannot determine the client identity. ProxySQL parses those address fields anyway via `sscanf` and writes the spoofed source address into the session's `addr.addr` field. From there it flows directly into the query-rule matcher, where the `client_addr` predicate decides routing and ACL. When `mysql-proxy_protocol_networks = '*'` (the default), any TCP peer can send a PP1 frame and choose any source IP claim. With that, any `mysql_query_rules` row pinned to a `client_addr` value is forgeable: the attacker writes the address they want to match into the PP1 line, and ProxySQL routes their query as if it came from that address. In practice this is a routing and ACL bypass. Real deployments use `client_addr` for read-write splitting (internal apps go to the primary, public traffic to read replicas), per-app schema pinning, and query-filter rules (DDL allowed only from admin CIDR, public queries blocked from dangerous patterns). An attacker that can reach the frontend port can forge their way into any of those routes. Version 3.0.9 patches this issue.

## References
- https://github.com/sysown/proxysql/releases/tag/v3.0.9
- https://github.com/sysown/proxysql/security/advisories/GHSA-gw94-85m2-x8v2
- https://nvd.nist.gov/vuln/detail/CVE-2026-48772
