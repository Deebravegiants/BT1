# [M] TypeBot: WhatsApp Webhook Endpoint Missing Signature Verification

## Summary
Severity: Medium
Advisory: CVE-2026-39969
Aliases: GHSA-8vqp-r5w7-v47f
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-05-22
Source: https://osv.dev/vulnerability/CVE-2026-39969
Type: osv

## Details
TypeBot is a chatbot builder tool. In versions 3.16.0 and prior, the WhatsApp Cloud API webhook endpoint (POST /v1/workspaces/{workspaceId}/whatsapp/{credentialsId}/webhook) does not verify the x-hub-signature-256 HMAC signature included by Meta in every webhook delivery. The webhook URL exposes both workspaceId and credentialsId as path parameters, which are logged in web server access logs, visible in Meta's webhook configuration dashboard, and potentially shared when configuring integrations. This allows any unauthenticated attacker to send spoofed webhook messages to trigger bot flows, consume API resources, and interact with external services using the workspace owner's credentials. The issue has been fixed in version 3.17.0.

## References
- https://github.com/baptisteArno/typebot.io/releases/tag/v3.17.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/39xxx/CVE-2026-39969.json
- https://github.com/baptisteArno/typebot.io/security/advisories/GHSA-8vqp-r5w7-v47f
- https://nvd.nist.gov/vuln/detail/CVE-2026-39969
