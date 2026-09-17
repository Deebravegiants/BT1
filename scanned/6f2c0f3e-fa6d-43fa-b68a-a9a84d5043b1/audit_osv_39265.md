# [H] MaxKB: Webhook Trigger Authentication Bypass

## Summary
Severity: High
Advisory: CVE-2026-44847
Aliases: GHSA-r3j3-j58q-rjpp
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-05-26
Source: https://osv.dev/vulnerability/CVE-2026-44847
Type: osv

## Details
MaxKB is an open-source AI assistant for enterprise. Prior to 2.9.0, MaxKB's webhook trigger endpoint (/api/trigger/v1/webhook/{trigger_id}) is accessible without authentication. The WebhookAuth class unconditionally returns (None, {}), which Django REST Framework interprets as successful authentication. Combined with optional per-trigger token verification and no backend enforcement of token requirements, any unauthenticated attacker who knows a valid trigger ID can invoke webhook triggers to execute their bound tasks. This vulnerability is fixed in 2.9.0.

## References
- https://github.com/1Panel-dev/MaxKB/security/advisories/GHSA-r3j3-j58q-rjpp
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44847.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-44847
- https://github.com/1Panel-dev/MaxKB/issues/5213
