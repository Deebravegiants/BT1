# [M] SiYuan before v3.8.1 Path Traversal via /api/template/render

## Summary
Severity: Medium
Advisory: CVE-2026-82650
Aliases: GHSA-9jfx-rc58-h23j
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:P/PR:H/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-30
Source: https://osv.dev/vulnerability/CVE-2026-82650
Type: osv

## Details
SiYuan 3.8.0 contains a path traversal / sensitive file exposure vulnerability in the RenderTemplate function (kernel/model/template.go), reachable via the POST /api/template/render endpoint (kernel/api/template.go). The endpoint restricts the supplied path only to the workspace directory (util.IsAbsPathInWorkspace) but, unlike the file API's refuseToAccess() blocklist, applies no sensitive-path exclusion. This allows an authenticated attacker to read sensitive workspace files, including conf/conf.json, which contains the API token and cookie signing key. The issue is fixed in v3.8.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82650.json
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-9jfx-rc58-h23j
- https://nvd.nist.gov/vuln/detail/CVE-2026-82650
- https://www.vulncheck.com/advisories/siyuan-before-3.8.1-path-traversal-via-api-template-render
