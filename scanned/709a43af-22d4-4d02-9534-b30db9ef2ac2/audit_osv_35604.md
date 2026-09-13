# [M] Hermes WebUI before 0.51.221 Path Traversal via Symlink Workspace Bypass

## Summary
Severity: Medium
Advisory: CVE-2026-11322
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-04
Source: https://osv.dev/vulnerability/CVE-2026-11322
Type: osv

## Details
Hermes WebUI prior to v0.51.221 contains a path traversal vulnerability that allows attackers to escape the workspace boundary by supplying symlinks that resolve to files or directories outside the designated workspace root. Attackers can exploit the workspace file and listing APIs, which resolve symlink targets without enforcing that the final path remains within the workspace, to read external host files accessible to the server process and disclose sensitive data such as SSH keys, cloud credentials, or application tokens.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/11xxx/CVE-2026-11322.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-11322
- https://www.vulncheck.com/advisories/hermes-webui-before-path-traversal-via-symlink-workspace-bypass
- https://github.com/nesquena/hermes-webui/pull/3398
- https://github.com/nesquena/hermes-webui/commit/7c48c376299b8058fd35127a59aefadded7e4a92
- https://github.com/nesquena/hermes-webui
