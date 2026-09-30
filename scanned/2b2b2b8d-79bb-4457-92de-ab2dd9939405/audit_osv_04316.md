# [H] terraform-mcp-server vulnerable to cross-user credential inheritance if an MCP session ID is obtained by another user

## Summary
Severity: High
Advisory: BIT-consul-2026-16496
Aliases: CVE-2026-16496
Ecosystem: Bitnami
Published: 2026-08-17
Source: https://osv.dev/vulnerability/BIT-consul-2026-16496
Type: osv

## Affected
- Bitnami: `consul` — affected >=0.3.0 <1.1.0

## Details
The terraform-mcp-server before version 1.1.0 is vulnerable to an authorization bypass in the streamable-HTTP stateful transport mode that may allow a user who obtains another user's MCP session ID to have their tool calls executed using that user's Terraform credentials. This vulnerability, CVE-2026-16496, is fixed in terraform-mcp-server 1.1.0.

## References
- https://discuss.hashicorp.com/t/hcsec-2026-23-multiple-vulnerabilities-impacting-hashicorp-terraform-mcp-server/77606
- https://nvd.nist.gov/vuln/detail/CVE-2026-16496
