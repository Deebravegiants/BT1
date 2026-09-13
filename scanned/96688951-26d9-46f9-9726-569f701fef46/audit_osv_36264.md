# [M] Hermes WebUI < 0.51.44 Path Traversal via Session Import Endpoint

## Summary
Severity: Medium
Advisory: CVE-2026-22677
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-05-13
Source: https://osv.dev/vulnerability/CVE-2026-22677
Type: osv

## Details
Hermes WebUI prior to 0.51.44 contains a path traversal vulnerability in the session import endpoint that allows authenticated attackers to read arbitrary files by importing a crafted session with an unrestricted workspace value. Attackers can supply a blocked filesystem root in the workspace field and subsequently use relative paths in the session file API to access any file readable by the WebUI process.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/22xxx/CVE-2026-22677.json
- https://github.com/nesquena/hermes-webui/releases/tag/v0.51.44
- https://nvd.nist.gov/vuln/detail/CVE-2026-22677
- https://www.vulncheck.com/advisories/hermes-webui-path-traversal-via-session-import-endpoint
- https://github.com/nesquena/hermes-webui/pull/2048
- https://github.com/nesquena/hermes-webui/commit/f00cb74f776f22f02f5eb6b39dfb389f87cc7fd3
- https://github.com/nesquena/hermes-webui
