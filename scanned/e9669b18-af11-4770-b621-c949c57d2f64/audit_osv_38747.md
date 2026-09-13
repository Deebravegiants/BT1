# [M] Dify < 1.14.2 Authorization Bypass via File Preview Endpoint

## Summary
Severity: Medium
Advisory: CVE-2026-41949
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-05-18
Source: https://osv.dev/vulnerability/CVE-2026-41949
Type: osv

## Details
Dify before version 1.14.2 contains an authorization bypass vulnerability in the file preview endpoint that allows any authenticated user to read up to 3,000 characters of any uploaded document across all tenants and workspaces using only the file's UUID. Attackers can access the /console/api/files/{file_id}/preview endpoint with an intercepted file UUID to extract sensitive content from documents without ownership or workspace permission verification. NOTE: Dify Cloud allows unauthenticated free self-registration, making account creation trivially accessible to any attacker.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41949.json
- https://github.com/langgenius/dify/releases/tag/1.14.2
- https://nvd.nist.gov/vuln/detail/CVE-2026-41949
- https://www.vulncheck.com/advisories/dify-authorization-bypass-via-file-preview-endpoint
- https://github.com/langgenius/dify/pull/35797
- https://github.com/langgenius/dify/commit/432a6412a3fdb30ce48003d699b90cc7d890df20
- https://huntr.com/bounties/d50a0240-7951-4939-b989-9bded66c7682
- https://www.zafran.io/resources/difytap-zafran-discovers-how-attackers-can-silently-wiretap-ai-data-across-tenants-on-a-platform-powering-1m-apps
