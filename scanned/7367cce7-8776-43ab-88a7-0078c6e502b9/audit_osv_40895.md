# [M] Capgo - Cross-Tenant Authorization Bypass via PostgREST Webhook Access

## Summary
Severity: Medium
Advisory: CVE-2026-56079
Aliases: GHSA-hj3h-v877-g5rx
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-19
Source: https://osv.dev/vulnerability/CVE-2026-56079
Type: osv

## Details
Capgo before 12.128.2 contains a cross-tenant authorization bypass vulnerability in PostgREST endpoints that allows org-scoped read API keys to access other tenants' webhook secrets and delivery logs. Attackers can query the webhooks and webhook_deliveries endpoints to exfiltrate HMAC signing secrets and delivery payloads, enabling forged webhook events against victim organizations.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56079.json
- https://github.com/Cap-go/capgo/security/advisories/GHSA-hj3h-v877-g5rx
- https://nvd.nist.gov/vuln/detail/CVE-2026-56079
- https://www.vulncheck.com/advisories/capgo-cross-tenant-authorization-bypass-via-postgrest-webhook-access
