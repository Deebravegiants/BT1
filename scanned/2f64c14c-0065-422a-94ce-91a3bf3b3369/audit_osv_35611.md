# [H] Markdown Preview Enhanced 0.8.x Code Injection via WaveDrom Rendering

## Summary
Severity: High
Advisory: CVE-2026-11422
CVSS: 7.5 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-05
Source: https://osv.dev/vulnerability/CVE-2026-11422
Type: osv

## Details
Markdown Preview Enhanced 0.8.x with crossnote engine 0.9.28 contains a code injection vulnerability in the WaveDrom rendering pipeline that allows attackers to execute arbitrary JavaScript by embedding malicious content in a wavedrom fenced code block within a crafted Markdown document. Attackers can exploit the unsanitized passing of wavedrom block content to window.eval() in the VS Code webview context to abuse the extension's message passing and invoke arbitrary file writes on the local filesystem.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/11xxx/CVE-2026-11422.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-11422
- https://www.vulncheck.com/advisories/markdown-preview-enhanced-x-code-injection-via-wavedrom-rendering
- https://github.com/shd101wyy/vscode-markdown-preview-enhanced/issues/2315
- https://github.com/shd101wyy/crossnote/commit/5588ca2121c3da43fe331575dc5cf4ef347b91ee
- https://github.com/shd101wyy/vscode-markdown-preview-enhanced/commit/dcd80281c986293b93d9f1af34ced64dcb230c77
- https://github.com/shd101wyy/crossnote
- https://github.com/shd101wyy/vscode-markdown-preview-enhanced
