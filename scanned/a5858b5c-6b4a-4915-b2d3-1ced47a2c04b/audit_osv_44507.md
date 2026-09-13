# [C] Devtron through 2.2.0 Missing Authorization via webhook API token endpoint

## Summary
Severity: Critical
Advisory: CVE-2026-82882
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-31
Source: https://osv.dev/vulnerability/CVE-2026-82882
Type: osv

## Details
Devtron through 2.2.0 fails to enforce authorization checks on the GET /orchestrator/api-token/webhook endpoint, allowing authenticated users to retrieve admin API tokens. Attackers with any authenticated account can query the endpoint with arbitrary project, environment, and application parameters to retrieve plaintext super-admin JWT tokens for full platform control.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82882.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-82882
- https://www.vulncheck.com/advisories/devtron-through-2.2.0-missing-authorization-via-webhook-api-token-endpoint
- https://github.com/devtron-labs/devtron/issues/7013
- https://github.com/devtron-labs/devtron
- https://github.com/devtron-labs/devtron/blob/v2.2.0/api/apiToken/ApiTokenRestHandler.go
- https://github.com/devtron-labs/devtron/blob/v2.2.0/pkg/apiToken/ApiTokenService.go
