# [H] Server-Side Request Forgery (SSRF) in Kibana Leading to Unauthorized Network Access

## Summary
Severity: High
Advisory: BIT-kibana-2026-42398
Aliases: BIT-elk-2026-42398, CVE-2026-42398
Ecosystem: Bitnami
Published: 2026-06-01
Source: https://osv.dev/vulnerability/BIT-kibana-2026-42398
Type: osv

## Affected
- Bitnami: `kibana` — affected >=9.3.0 <9.3.2

## Details
Server-Side Request Forgery (CWE-918) in Kibana allows authenticated users with connector management privileges to bypass the operator-configured connection allowlist. By configuring a Webhook connector with a crafted target, an attacker can cause Kibana to issue outbound requests to destinations that the egress restriction controls were intended to block.

## References
- https://discuss.elastic.co/t/kibana-9-2-8-and-9-3-2-security-update-esa-2026-37/386557
- https://nvd.nist.gov/vuln/detail/CVE-2026-42398
