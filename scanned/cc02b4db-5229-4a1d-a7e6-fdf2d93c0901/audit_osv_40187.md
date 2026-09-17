# [C] Markdown Preview Enhanced Arbitrary Code Execution via WaveDrom eval()

## Summary
Severity: Critical
Advisory: CVE-2026-50733
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-05
Source: https://osv.dev/vulnerability/CVE-2026-50733
Type: osv

## Details
Markdown Preview Enhanced before 0.8.28 parses WaveDrom diagrams by evaluating untrusted markdown content with eval(), allowing arbitrary JavaScript execution. The flaw affects every render path - the live preview (window.eval) and presentation mode plus HTML export (the bundled WaveDrom.ProcessAll()/eva() helpers) - and can also be triggered through a <script type="WaveDrom"> element injected via raw HTML in markdown. When a victim previews or exports a crafted markdown document, an attacker can execute arbitrary code, leading to arbitrary file write. Fixed in 0.8.28 by parsing with JSON5.parse() and sanitizing WaveDrom data scripts to inert strict JSON.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/50xxx/CVE-2026-50733.json
- https://github.com/shd101wyy/vscode-markdown-preview-enhanced/releases/tag/0.8.28
- https://nvd.nist.gov/vuln/detail/CVE-2026-50733
- https://www.vulncheck.com/advisories/markdown-preview-enhanced-arbitrary-code-execution-via-wavedrom-eval
- https://github.com/shd101wyy/vscode-markdown-preview-enhanced/issues/2315
