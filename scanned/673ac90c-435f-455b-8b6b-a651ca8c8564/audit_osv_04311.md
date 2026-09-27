# [H] terraform-mcp-server vulnerable to server side request forgery leading to token exposure

## Summary
Severity: High
Advisory: BIT-consul-2026-14869
Aliases: CVE-2026-14869
Ecosystem: Bitnami
Published: 2026-08-17
Source: https://osv.dev/vulnerability/BIT-consul-2026-14869
Type: osv

## Affected
- Bitnami: `consul` — affected >=0.3.0 <1.1.0

## Details
The terraform-mcp-server before version 1.1.0 is vulnerable to a server-side request forgery issue in the streamable-HTTP transport that may allow an unauthenticated remote client to redirect the server's Terraform API requests, and the server-side authorization token, to an attacker-controlled endpoint. This vulnerability, CVE-2026-14869, is fixed in terraform-mcp-server 1.1.0.

## References
- https://discuss.hashicorp.com/t/hcsec-2026-23-multiple-vulnerabilities-impacting-hashicorp-terraform-mcp-server/77606
- https://nvd.nist.gov/vuln/detail/CVE-2026-14869
