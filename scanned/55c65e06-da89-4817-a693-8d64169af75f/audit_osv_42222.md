# [M] Void 1.3.4 Path Traversal via AI Agent File-Reading Tools

## Summary
Severity: Medium
Advisory: CVE-2026-65698
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:P/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-23
Source: https://osv.dev/vulnerability/CVE-2026-65698
Type: osv

## Details
Void through 1.3.4 contains a path traversal vulnerability in the AI agent file-reading tools that allows network-adjacent attackers to read arbitrary host files outside the open workspace by injecting instructions into content the agent processes. Attackers can supply absolute paths or file:// URIs through the read_file, ls_dir, get_dir_tree, and search_* tools, which lack workspace confinement and bypass the approval gate, enabling silent exfiltration of sensitive files such as SSH private keys or cloud credentials via subsequent tool calls.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/65xxx/CVE-2026-65698.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-65698
- https://www.vulncheck.com/advisories/void-path-traversal-via-ai-agent-file-reading-tools
- https://github.com/voideditor/void
- https://github.com/geo-chen/oss/blob/main/void.md
