# [M] AutoGPT: IDOR in Webhook Ping Endpoint Allows Enumeration and Cross-User Ping Triggering

## Summary
Severity: Medium
Advisory: CVE-2026-56823
Aliases: GHSA-rq9m-xvc7-v9h6
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-06-26
Source: https://osv.dev/vulnerability/CVE-2026-56823
Type: osv

## Details
AutoGPT is a workflow automation platform for creating, deploying, and managing continuous artificial intelligence agents. Prior to , the `POST /api/integrations/webhooks/{webhook_id}/ping` endpoint fetches the target webhook by primary key alone without verifying that the webhook belongs to the authenticated user. Any authenticated user can supply an arbitrary webhook_id to confirm webhook existence, leak the webhook's OAuth provider type, and in some cases trigger a ping delivery on behalf of another user. This vulnerability is fixed in .

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56823.json
- https://github.com/Significant-Gravitas/AutoGPT/security/advisories/GHSA-rq9m-xvc7-v9h6
- https://nvd.nist.gov/vuln/detail/CVE-2026-56823
