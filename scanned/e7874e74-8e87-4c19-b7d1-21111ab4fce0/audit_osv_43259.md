# [H] AutoGPT: Webhook provider path confusion bypasses generic webhook secret verification

## Summary
Severity: High
Advisory: CVE-2026-72922
Aliases: GHSA-349p-3c3r-8mjr
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:N)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-72922
Type: osv

## Details
AutoGPT is a workflow automation platform for creating, deploying, and managing continuous artificial intelligence agents. Prior to 0.6.70, AutoGPT's autogpt_platform/backend/backend/api/features/integrations/router.py webhook_ingress_generic route selected get_webhook_manager(provider) from the untrusted provider URL segment without verifying webhook.provider, allowing a request to /compass/webhooks/{webhook_id}/ingress to use CompassWebhookManager's inherited no-op BaseWebhooksManager.verify_signature instead of GenericWebhooksManager.verify_signature, bypass X-Webhook-Secret for a configured secret_token, and execute a generic webhook graph as its owner. This issue is fixed in version 0.6.70.

## References
- https://github.com/Significant-Gravitas/AutoGPT/releases/tag/autogpt-platform-beta-v0.6.70
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72922.json
- https://github.com/Significant-Gravitas/AutoGPT/security/advisories/GHSA-349p-3c3r-8mjr
- https://nvd.nist.gov/vuln/detail/CVE-2026-72922
- https://github.com/Significant-Gravitas/AutoGPT/commit/646dd5b8cfad1206e92ec7bcc3b8312657e2a92e
- https://github.com/Significant-Gravitas/AutoGPT/pull/13559
