# [C] Markdown Preview Enhanced OS Command Injection in External File and Link Opening

## Summary
Severity: Critical
Advisory: CVE-2026-49492
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-05
Source: https://osv.dev/vulnerability/CVE-2026-49492
Type: osv

## Details
Markdown Preview Enhanced before 0.8.28 opens external files and links from the preview through a shell and does not validate untrusted inputs taken from the markdown document - the diagram filename attribute, imported file paths, and the latex_engine code-chunk attribute. On Windows, a crafted markdown document can inject operating system commands that execute when the document is previewed. Fixed in 0.8.28 by passing these inputs as literal arguments instead of through a shell and validating them before use.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/49xxx/CVE-2026-49492.json
- https://github.com/shd101wyy/vscode-markdown-preview-enhanced/releases/tag/0.8.28
- https://nvd.nist.gov/vuln/detail/CVE-2026-49492
- https://www.vulncheck.com/advisories/markdown-preview-enhanced-os-command-injection-in-external-file-and-link-opening
