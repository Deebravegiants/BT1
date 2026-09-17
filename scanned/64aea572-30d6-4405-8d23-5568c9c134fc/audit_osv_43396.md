# [H] Trigger.dev: Cross-tenant object store read and write via URL path traversal

## Summary
Severity: High
Advisory: CVE-2026-73658
Aliases: GHSA-888c-px7m-736v
CVSS: 8.2 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:N)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/CVE-2026-73658
Type: osv

## Details
Trigger.dev is a platform for building and deploying fully managed AI agents and workflows. From 4.4.2 until 4.5.0-rc.5, Aws4FetchClient.buildUrl() and Aws4FetchClient.presign() in apps/webapp/app/v3/objectStoreClient.server.ts assign user-controlled packet keys to URL.pathname, while apps/webapp/app/routes/api.v1.packets.$.ts accepts params["*"] without rejecting dot segments and uses findResource: async () => 1 without per-resource ownership validation. WHATWG path normalization collapses .. segments before signing, allowing a caller with a valid environment API key to obtain presigned URLs for another tenant's object-store keys and read or overwrite task payloads. This issue is fixed in version 4.5.0-rc.5.

## References
- https://github.com/triggerdotdev/trigger.dev/releases/tag/v4.5.0-rc.5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73658.json
- https://github.com/triggerdotdev/trigger.dev/security/advisories/GHSA-888c-px7m-736v
- https://nvd.nist.gov/vuln/detail/CVE-2026-73658
- https://github.com/triggerdotdev/trigger.dev/commit/db4074df54db06b0656becf3f974345c90fa202e
- https://github.com/triggerdotdev/trigger.dev/pull/3830
