# [C] TypeBot: Unauthenticated SSRF via isolated-vm fetch in preview chat endpoint bypasses SSRF controls

## Summary
Severity: Critical
Advisory: CVE-2026-33712
Aliases: GHSA-vc2q-r6rq-ggj9
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:N)
Published: 2026-05-22
Source: https://osv.dev/vulnerability/CVE-2026-33712
Type: osv

## Details
Typebot is a chatbot builder tool. In versions 3.15.2 and prior, the preview chat endpoint (POST /api/v1/typebots/{typebotId}/preview/startChat) allows unauthenticated users to achieve Server-Side Request Forgery (SSRF) by supplying a custom typebot definition with server-side code blocks. The fetch function exposed inside the isolated-vm sandbox calls Node.js native fetch without the SSRF validation (validateHttpReqUrl) that protects the HTTP Request block. This bypasses all SSRF mitigations added after GHSA-8gq9-rw7v-3jpr. Exploitation of this unauthenticated SSRF vulnerability can lead to cloud credential theft, internal network access and data exfiltration for any self-hosted Typebot deployments and hosted services. This issue has been fixed in version 3.16.0.

## References
- https://github.com/baptisteArno/typebot.io/releases/tag/v3.16.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33712.json
- https://github.com/baptisteArno/typebot.io/security/advisories/GHSA-vc2q-r6rq-ggj9
- https://nvd.nist.gov/vuln/detail/CVE-2026-33712
