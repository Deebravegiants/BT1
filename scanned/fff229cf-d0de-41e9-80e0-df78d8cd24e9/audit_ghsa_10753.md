# [H] External Secrets Operator has DNS-based secret exfiltration via getHostByName in External Secrets v2 template engine

## Summary
Severity: High
Advisory: GHSA-r2pg-r6h7-crf3
CVE: CVE-2026-34984
CWE: CWE-200
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-04-13
Source: https://github.com/advisories/GHSA-r2pg-r6h7-crf3
Type: github-advisory

## Affected
- Go: `github.com/external-secrets/external-secrets` — affected >=0 <1.3.3-0.20260331202714-6800989bdc12
- Go: `github.com/external-secrets/external-secrets` — affected >=2.0.0

## Details
## Summary

The v2 template engine in `runtime/template/v2/template.go` imports Sprig’s `TxtFuncMap()` and removes `env` and `expandenv`, but leaves `getHostByName` available to user-controlled  templates. Because ESO executes templates inside the controller process, an attacker who can create or update templated ExternalSecret resources can trigger controller-side DNS lookups using secret-derived values, creating a DNS exfiltration primitive.

### Impact
This is a confidentiality issue. In environments where untrusted or lower-trust users can author templated ExternalSecret resources and the controller can perform DNS resolution, fetched secret material can be exfiltrated through DNS without requiring direct outbound access from the attacker’s workload.

## References
- https://github.com/external-secrets/external-secrets/security/advisories/GHSA-r2pg-r6h7-crf3
- https://nvd.nist.gov/vuln/detail/CVE-2026-34984
- https://github.com/external-secrets/external-secrets/commit/6800989bdc12782ca2605d3b8bf7f2876a16551a
- https://github.com/external-secrets/external-secrets
- https://github.com/external-secrets/external-secrets/releases/tag/v2.3.0
