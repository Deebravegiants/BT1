# [C] Terraform Provider for SendGrid: TLS Session Resumption Bypasses Certificate Authority Trust Store Modifications in Go

## Summary
Severity: Critical
Advisory: GHSA-j443-wcqq-xprh
CWE: CWE-295
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-11
Source: https://github.com/advisories/GHSA-j443-wcqq-xprh
Type: github-advisory

## Affected
- Go: `github.com/arslanbekov/terraform-provider-sendgrid` — affected >=0

## Details
### Summary

A critical vulnerability has been identified at https://security.snyk.io/package/linux/chainguard:latest/terraform-provider-sendgrid, associated with the underlying Go version.

If the server's TLS configuration is mutated between connections — for example, a CA is removed from the trusted list via `Config.Clone()` combined with modification or `GetConfigForClient` — the resumed handshake still succeeds using the cached session. The certificate is not re-checked against the updated CA list.

As a result, a client whose CA was revoked or removed between the first and second connection could still establish a connection on the resumed session.

### Details

If the server's TLS configuration is mutated between connections — for example, a CA is removed from the trusted list via `Config.Clone()` combined with modification or `GetConfigForClient` — the resumed handshake still succeeds using the cached session. The certificate is not re-checked against the updated CA list.

Consequently, a client whose CA was revoked or removed between the first and second connection could still establish a connection on the resumed session.

## References
- https://github.com/arslanbekov/terraform-provider-sendgrid/security/advisories/GHSA-j443-wcqq-xprh
- https://github.com/advisories/GHSA-h355-32pf-p2xm
- https://github.com/arslanbekov/terraform-provider-sendgrid
- https://security.snyk.io/vuln/SNYK-CHAINGUARDLATEST-TERRAFORMPROVIDERSENDGRID-15265295
