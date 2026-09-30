# [M] Discourse doesn't ensure webhooks require a token

## Summary
Severity: Medium
Advisory: BIT-discourse-2026-26077
Aliases: CVE-2026-26077, GHSA-j67c-53j2-4hfw
Ecosystem: Bitnami
Published: 2026-03-03
Source: https://osv.dev/vulnerability/BIT-discourse-2026-26077
Type: osv

## Affected
- Bitnami: `discourse` — affected >=2026.1.0 <2026.1.1

## Details
Discourse is an open source discussion platform. Prior to versions 2025.12.2, 2026.1.1, and 2026.2.0, several webhook endpoints (SendGrid, Mailjet, Mandrill, Postmark, SparkPost) in the `WebhooksController` accepted requests without a valid authentication token when no token was configured. This allowed unauthenticated attackers to forge webhook payloads and artificially inflate user bounce scores, potentially causing legitimate user emails to be disabled. The Mailpace endpoint had no token validation at all. Starting in versions 2025.12.2, 2026.1.1, and 2026.2.0, all webhook endpoints reject requests with a 406 response when no authentication token is configured. As a workaround, ensure that webhook authentication tokens are configured for all email provider integrations in site settings (e.g., `sendgrid_verification_key`, `mailjet_webhook_token`, `postmark_webhook_token`, `sparkpost_webhook_token`). There's no current workaround for mailpace before getting this fix.

## References
- https://github.com/discourse/discourse/security/advisories/GHSA-j67c-53j2-4hfw
- https://nvd.nist.gov/vuln/detail/CVE-2026-26077
