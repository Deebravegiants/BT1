# [M] Capgo - Webhook Signing Secret Disclosure via Non-Admin API Key

## Summary
Severity: Medium
Advisory: CVE-2026-56244
Aliases: GHSA-qrrx-x3qf-x87v
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-56244
Type: osv

## Details
Capgo before 12.128.2 allows non-admin API keys to read webhook signing secrets via Supabase REST due to insufficient row-level security policies on the webhooks table. Attackers can retrieve the webhook secret and forge valid X-Capgo-Signature headers to send authenticated webhook events to configured receivers, breaking webhook authenticity and integrity.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56244.json
- https://github.com/Cap-go/capgo/security/advisories/GHSA-qrrx-x3qf-x87v
- https://nvd.nist.gov/vuln/detail/CVE-2026-56244
- https://www.vulncheck.com/advisories/capgo-webhook-signing-secret-disclosure-via-non-admin-api-key
