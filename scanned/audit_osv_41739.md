# [C] GPT-SoVITS 20250606v2pro OS Command Injection via webui.py

## Summary
Severity: Critical
Advisory: CVE-2026-63766
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-20
Source: https://osv.dev/vulnerability/CVE-2026-63766
Type: osv

## Details
GPT-SoVITS through 20250606v2pro contains an OS command injection vulnerability in webui.py where ASR, slice, denoise, and uvr5 functions interpolate unsanitized Gradio textbox values directly into shell commands executed with shell=True. Attackers can inject shell metacharacters through path parameters to execute arbitrary OS commands as the server process user without authentication.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63766.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63766
- https://www.vulncheck.com/advisories/gpt-sovits-20250606v2pro-os-command-injection-via-webui-py
- https://github.com/RVC-Boss/GPT-SoVITS/issues/2793
- https://github.com/RVC-Boss/GPT-SoVITS
