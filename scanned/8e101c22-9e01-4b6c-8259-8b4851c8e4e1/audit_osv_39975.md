# [H] TypeBot has SSRF in HTTP request and script fetch flows via DNS rebinding bypass

## Summary
Severity: High
Advisory: CVE-2026-48764
Aliases: GHSA-hgqq-whf5-mrrf
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N)
Published: 2026-06-17
Source: https://osv.dev/vulnerability/CVE-2026-48764
Type: osv

## Details
TypeBot is a chatbot builder tool. In versions prior to 3.17.2, SSRF validation is implemented by resolving a hostname once and checking whether the resolved IP belongs to a forbidden range allowing for DNS rebinding bypass. The root cause is a time-of-check to time-of-use gap in the SSRF guard. The validator resolves the hostname and approves it, but the later request path performs a fresh resolution and connects to whatever IP the hostname maps to at that moment. The actual outbound request is then performed later using the original hostname, without pinning the validated IP to the network connection. An attacker who can supply a URL to a public bot that performs a server-side HTTP Request block or server-side script fetch can use DNS rebinding to pass the initial validation and still force the server to connect to a private or metadata address during the real request. This enables server-side access to private network services, cloud metadata endpoints, and other internal HTTP targets that the validator was intended to block. The exact downstream impact depends on the reachable internal services. Concrete consequences include metadata disclosure, access to internal admin panels, credential theft from metadata services, and further compromise through internal-only HTTP interfaces. This issue has been fixed in version 3.17.2.

## References
- https://github.com/baptisteArno/typebot.io/releases/tag/v3.17.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48764.json
- https://github.com/baptisteArno/typebot.io/security/advisories/GHSA-hgqq-whf5-mrrf
- https://nvd.nist.gov/vuln/detail/CVE-2026-48764
- https://github.com/baptisteArno/typebot.io/commit/f56c3c3f771df13a8c11e88f500dfdd78981bed1
