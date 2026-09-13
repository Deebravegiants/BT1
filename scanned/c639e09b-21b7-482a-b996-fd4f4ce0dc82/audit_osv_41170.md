# [C] Hermes WebUI < 0.51.788 Unauthenticated RCE via Terminal API

## Summary
Severity: Critical
Advisory: CVE-2026-58123
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-09
Source: https://osv.dev/vulnerability/CVE-2026-58123
Type: osv

## Details
Hermes WebUI before 0.51.788 contains an unauthenticated remote code execution vulnerability that allows remote attackers to execute arbitrary shell commands by accessing the embedded terminal API endpoints without credentials. Attackers can create a session, attach a PTY shell, and write arbitrary commands through the terminal input endpoint to achieve full command execution as the server process user via four sequential unauthenticated HTTP requests.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/58xxx/CVE-2026-58123.json
- https://github.com/nesquena/hermes-webui/releases/tag/v0.51.788
- https://nvd.nist.gov/vuln/detail/CVE-2026-58123
- https://www.vulncheck.com/advisories/hermes-webui-unauthenticated-rce-via-terminal-api
- https://github.com/nesquena/hermes-webui/pull/5268
- https://github.com/nesquena/hermes-webui/commit/d257e5f36cfa9328600c8bde6f0de09a6ad9b6f4
- https://github.com/nesquena/hermes-webui
