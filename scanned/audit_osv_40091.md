# [C] Markdown Preview Enhanced Arbitrary Code Execution via Bitfield interpretJS()

## Summary
Severity: Critical
Advisory: CVE-2026-49493
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-05
Source: https://osv.dev/vulnerability/CVE-2026-49493
Type: osv

## Details
Markdown Preview Enhanced before 0.8.28 parses Bitfield fenced code blocks with interpretJS(), which evaluates the block content as code via vm.runInNewContext(), allowing arbitrary code execution. A crafted markdown document containing a malicious bitfield code block executes attacker-controlled code on the server side when the document is rendered or exported. Fixed in 0.8.28 by parsing bitfield register definitions with JSON5.parse(), since they are purely data.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/49xxx/CVE-2026-49493.json
- https://github.com/shd101wyy/vscode-markdown-preview-enhanced/releases/tag/0.8.28
- https://nvd.nist.gov/vuln/detail/CVE-2026-49493
- https://www.vulncheck.com/advisories/markdown-preview-enhanced-arbitrary-code-execution-via-bitfield-interpretjs
