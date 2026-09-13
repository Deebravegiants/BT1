# [M] Dify < 1.14.0 Authorization Bypass via File UUID

## Summary
Severity: Medium
Advisory: CVE-2026-41950
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-05-05
Source: https://osv.dev/vulnerability/CVE-2026-41950
Type: osv

## Details
Dify before version 1.14.0 contains an authorization bypass vulnerability that allows authenticated users to read the full contents of files uploaded by other users within the same tenant by supplying an arbitrary file UUID in the files array of a chat-messages request. Attackers can exploit insufficient permission verification in the chat-messages endpoints to access files without ownership validation, bypassing workspace separation and signed URL protections to retrieve sensitive file contents through workflow processing.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41950.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-41950
- https://www.vulncheck.com/advisories/dify-authorization-bypass-via-file-uuid
- https://github.com/langgenius/dify/releases/tag/1.14.0
- https://huntr.com/bounties/181136ec-d957-4b75-8ea7-6fa7b8abd01d
- https://www.zafran.io/resources/difytap-zafran-discovers-how-attackers-can-silently-wiretap-ai-data-across-tenants-on-a-platform-powering-1m-apps
