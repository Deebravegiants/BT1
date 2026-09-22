# [C] Skyvern before 1.0.45 Sandbox Escape via TextPromptBlock

## Summary
Severity: Critical
Advisory: CVE-2026-82447
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-29
Source: https://osv.dev/vulnerability/CVE-2026-82447
Type: osv

## Details
Skyvern before 1.0.45 contains a sandbox escape vulnerability in TextPromptBlock that renders prompts twice, first through a sandboxed Jinja environment and then through an unsandboxed environment. Attackers can inject malicious Jinja template syntax through workflow parameters or upstream block output to execute arbitrary code with server process privileges.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82447.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-82447
- https://www.vulncheck.com/advisories/skyvern-before-1.0.45-sandbox-escape-via-textpromptblock
- https://github.com/Skyvern-AI/skyvern/commit/d723de621d5b3a340f3cc4d5b46bfe40a9a3124e
- https://github.com/Skyvern-AI/skyvern
- https://github.com/Skyvern-AI/skyvern/blob/v1.0.44/skyvern/forge/sdk/prompting.py
- https://github.com/Skyvern-AI/skyvern/blob/v1.0.44/skyvern/forge/sdk/workflow/models/block.py
