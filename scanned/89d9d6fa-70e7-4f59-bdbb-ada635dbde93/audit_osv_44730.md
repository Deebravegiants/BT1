# [C] aider 0.86.2 Remote Code Execution via .aider.conf.yml

## Summary
Severity: Critical
Advisory: CVE-2026-85674
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-04
Source: https://osv.dev/vulnerability/CVE-2026-85674
Type: osv

## Details
aider (aider-chat) automatically loads a .aider.conf.yml configuration file from the root of the git repository it is launched in. A crafted repository can set test-cmd (executed at startup) or lint-cmd (executed on the first file edit), which aider runs through a shell (subprocess with shell=True) without any user confirmation, LLM interaction, or API key. Consequently, a user who clones and runs aider inside an attacker-supplied repository achieves arbitrary command execution on their machine. The behavior is long-standing and was confirmed on 0.86.3.dev (current main).

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85674.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-85674
- https://www.vulncheck.com/advisories/aider-0.86.2-remote-code-execution-via-aider-conf-yml
- https://github.com/Aider-AI/aider/issues/5254
- https://github.com/Aider-AI/aider
- https://github.com/Aider-AI/aider/blob/v0.86.2/aider/main.py
