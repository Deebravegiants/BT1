# [H] Coolify: Unauthenticated Deployment Trigger via Webhook HMAC Bypass with Null Secret

## Summary
Severity: High
Advisory: CVE-2026-41896
Aliases: GHSA-w8wm-r924-f65v
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-06-29
Source: https://osv.dev/vulnerability/CVE-2026-41896
Type: osv

## Details
Coolify is an open-source and self-hostable tool for managing servers, applications, and databases. Prior to 4.0.0-beta.474, the HMAC key is the application's manual_webhook_secret_github field, which is used by Coolify's webhook endpoints to validate incoming requests, is nullable with no default — meaning newly created applications have a null webhook secret. PHP's hash_hmac() function silently coerces a null key to an empty string ''. So when the secret is null, the server computes hash_hmac('sha256', $payload, '') — a deterministic value that any attacker can calculate independently. By sending X-Hub-Signature-256: sha256=<hash_hmac('sha256', payload, '')>, an unauthenticated attacker can forge a valid signature and trigger deployments. This vulnerability is fixed in 4.0.0-beta.474.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41896.json
- https://github.com/coollabsio/coolify/security/advisories/GHSA-w8wm-r924-f65v
- https://nvd.nist.gov/vuln/detail/CVE-2026-41896
