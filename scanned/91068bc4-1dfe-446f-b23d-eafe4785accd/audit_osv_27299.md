# [H] Command Injection in gradio-app/gradio via deploy+test-visual.yml workflow

## Summary
Severity: High
Advisory: CVE-2024-1540
CVSS: 8.6 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:L)
Published: 2024-03-27
Source: https://osv.dev/vulnerability/CVE-2024-1540
Type: osv

## Details
A command injection vulnerability exists in the deploy+test-visual.yml workflow of the gradio-app/gradio repository, due to improper neutralization of special elements used in a command. This vulnerability allows attackers to execute unauthorized commands, potentially leading to unauthorized modification of the base repository or secrets exfiltration. The issue arises from the unsafe handling of GitHub context information within a `run` operation, where expressions inside `${{ }}` are evaluated and substituted before script execution. Remediation involves setting untrusted input values to intermediate environment variables to prevent direct influence on script generation.

## References
- https://huntr.com/bounties/0e39e974-9a66-476f-91f5-3f37abb03d77
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/1xxx/CVE-2024-1540.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-1540
- https://github.com/gradio-app/gradio/commit/d56bb28df80d8db1f33e4acf4f6b2c4f87cb8b28
