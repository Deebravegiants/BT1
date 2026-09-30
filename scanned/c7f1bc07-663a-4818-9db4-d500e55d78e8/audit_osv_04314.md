# [C] consul-mcp-server vulnerable to cross-tenant credential reuse in streamable-HTTP stateless mode

## Summary
Severity: Critical
Advisory: BIT-consul-2026-16326
Aliases: CVE-2026-16326
Ecosystem: Bitnami
Published: 2026-08-17
Source: https://osv.dev/vulnerability/BIT-consul-2026-16326
Type: osv

## Affected
- Bitnami: `consul` — affected >=0.1.0 <0.1.4

## Details
In consul-mcp-server, versions 0.1.0 up to 0.1.3 did not properly isolate session state in stateless mode, which may allow one client's Consul authentication token to be used for subsequent requests from other clients. This vulnerability (CVE-2026-16326) is fixed in consul-mcp-server 0.1.4.

## References
- https://discuss.hashicorp.com/t/hcsec-2026-24-multiple-vulnerabilities-impacting-hashicorp-consul-mcp-server/77612
- https://nvd.nist.gov/vuln/detail/CVE-2026-16326
