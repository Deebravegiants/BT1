# [H] consul-mcp-server vulnerable to server side request forgery leading to token exposure

## Summary
Severity: High
Advisory: BIT-consul-2026-16328
Aliases: CVE-2026-16328
Ecosystem: Bitnami
Published: 2026-08-17
Source: https://osv.dev/vulnerability/BIT-consul-2026-16328
Type: osv

## Affected
- Bitnami: `consul` — affected >=0.1.0 <0.1.4

## Details
In consul-mcp-server, versions 0.1.0 up to 0.1.3 did not restrict how the Consul backend address was supplied, allowing a connected client to override the server's configured Consul address via a request header. This may allow a malicious client to redirect the server's Consul API traffic to an attacker-controlled endpoint, potentially exfiltrating the Consul token configured on the server. This vulnerability, CVE-2026-16328, is fixed in consul-mcp-server 0.1.4.

## References
- https://discuss.hashicorp.com/t/hcsec-2026-24-multiple-vulnerabilities-impacting-hashicorp-consul-mcp-server/77612
- https://nvd.nist.gov/vuln/detail/CVE-2026-16328
