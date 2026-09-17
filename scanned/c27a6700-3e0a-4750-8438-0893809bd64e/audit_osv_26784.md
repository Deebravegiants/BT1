# [C] Codigo Markdown Editor 1.0.1 Electron Arbitrary Code Execution via Markdown File

## Summary
Severity: Critical
Advisory: CVE-2023-53940
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2025-12-18
Source: https://osv.dev/vulnerability/CVE-2023-53940
Type: osv

## Details
Codigo Markdown Editor 1.0.1 contains a code execution vulnerability that allows attackers to run arbitrary system commands by crafting a malicious markdown file. Attackers can embed a video source with an onerror event that executes shell commands through Node.js child_process module when the file is opened.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53940.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53940
- https://www.vulncheck.com/advisories/codigo-markdown-editor-electron-arbitrary-code-execution-via-markdown-file
- https://github.com/alfonzm/codigo-app
- https://www.exploit-db.com/exploits/51432
