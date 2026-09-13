# [H] TypeBot: SSRF protection bypass via IPv6 unspecified address in Typebot HTTP request execution

## Summary
Severity: High
Advisory: CVE-2026-49213
Aliases: GHSA-qx46-p88f-xxm3
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-07-10
Source: https://osv.dev/vulnerability/CVE-2026-49213
Type: osv

## Details
TypeBot is a chatbot builder tool. Prior to 3.17.2, Typebot's shared SSRF validator in packages/lib/src/ssrf/validateHttpReqUrl.ts can be bypassed with the IPv6 unspecified address :: because validateIPAddress blocks local, metadata, and private ranges but does not block :: or its expanded form. A workspace editor or creator can configure a server-side HTTP Request block or guarded script fetch to make the Typebot server connect to local HTTP services through safeKy, including flows triggered by POST /v1/typebots/{publicId}/startChat or POST /v1/sessions/{sessionId}/continueChat. This issue is fixed in version 3.17.2.

## References
- https://github.com/baptisteArno/typebot.io/releases/tag/v3.17.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/49xxx/CVE-2026-49213.json
- https://github.com/baptisteArno/typebot.io/security/advisories/GHSA-qx46-p88f-xxm3
- https://nvd.nist.gov/vuln/detail/CVE-2026-49213
- https://github.com/baptisteArno/typebot.io/commit/f56c3c3f771df13a8c11e88f500dfdd78981bed1
- https://github.com/baptisteArno/typebot.io/pull/2511
