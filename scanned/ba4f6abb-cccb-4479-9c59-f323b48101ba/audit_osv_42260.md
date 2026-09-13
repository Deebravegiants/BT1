# [C] SiYuan before v3.7.2 Unauthenticated Administrator Takeover via MCP

## Summary
Severity: Critical
Advisory: CVE-2026-66012
Aliases: GHSA-cvhv-7xhj-xjp8
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-66012
Type: osv

## Details
SiYuan before v3.7.2 contains a missing authorization vulnerability in the POST /mcp kernel endpoint, which is gated only by a general auth check (model.CheckAuth) with no admin-role or read-only enforcement. This exposes 31 MCP tools, including a file tool with list/read/write/delete/rename/copy actions across the entire workspace. When the Publish server is enabled in anonymous mode (Conf.Publish.Enable=true and Conf.Publish.Auth.Enable=false), the Publish reverse proxy attaches an anonymous RoleReader JWT to proxied requests, allowing a remote unauthenticated attacker to reach /mcp. The attacker can read conf/conf.json to extract accessAuthCode, api.token, and cookieKey in plaintext, write arbitrary files in the workspace, and plant a plugin into data/plugins/ that executes with nodeIntegration:true and no contextIsolation on the next desktop launch, leading to administrator takeover.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/66xxx/CVE-2026-66012.json
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-cvhv-7xhj-xjp8
- https://nvd.nist.gov/vuln/detail/CVE-2026-66012
- https://www.vulncheck.com/advisories/siyuan-before-unauthenticated-administrator-takeover-via-mcp
- https://github.com/siyuan-note/siyuan/commit/c72ca4cd09019e5f64afdee8f8c6ec5ef34858db
