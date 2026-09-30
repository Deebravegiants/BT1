# [H] Roo Code: Potential Remote Code Execution via Bash Parameter Expansion and Indirect Reference

## Summary
Severity: High
Advisory: CVE-2025-58370
Aliases: GHSA-2rm5-cvcm-7592
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-05
Source: https://osv.dev/vulnerability/CVE-2025-58370
Type: osv

## Details
Roo Code is an AI-powered autonomous coding agent that lives in users' editors. Versions below 3.26.0 contain a vulnerability in the command parsing logic where the Bash parameter expansion and indirect reference were not handled correctly. If the agent was configured to auto-approve execution of certain commands, an attacker able to influence prompts could abuse this weakness to execute additional arbitrary commands alongside the intended one. This is fixed in version 3.26.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/58xxx/CVE-2025-58370.json
- https://github.com/RooCodeInc/Roo-Code/security/advisories/GHSA-2rm5-cvcm-7592
- https://nvd.nist.gov/vuln/detail/CVE-2025-58370
