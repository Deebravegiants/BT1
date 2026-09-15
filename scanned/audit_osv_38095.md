# [M] Postiz: SSRF via Webhook Creation Endpoint Missing URL Safety Validation

## Summary
Severity: Medium
Advisory: CVE-2026-34590
Aliases: GHSA-wc9c-7cv8-m225
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-04-02
Source: https://osv.dev/vulnerability/CVE-2026-34590
Type: osv

## Details
Postiz is an AI social media scheduling tool. Prior to version 2.21.4, the POST /webhooks/ endpoint for creating webhooks uses WebhooksDto which validates the url field with only @IsUrl() (format check), missing the @IsSafeWebhookUrl validator that blocks internal/private network addresses. The update (PUT /webhooks/) and test (POST /webhooks/send) endpoints correctly apply @IsSafeWebhookUrl. When a post is published, the orchestrator fetches the stored webhook URL without runtime validation, enabling blind SSRF against internal services. This issue has been patched in version 2.21.4.

## References
- https://github.com/gitroomhq/postiz-app/releases/tag/v2.21.4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34590.json
- https://github.com/gitroomhq/postiz-app/security/advisories/GHSA-wc9c-7cv8-m225
- https://nvd.nist.gov/vuln/detail/CVE-2026-34590
- https://github.com/gitroomhq/postiz-app/commit/5ae4c950db6aa516a31454b7a45b9480bca40a11
