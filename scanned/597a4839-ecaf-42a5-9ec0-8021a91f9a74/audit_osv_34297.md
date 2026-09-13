# [H] Roo-Code potential remote code execution via auto-execute command parsing flaw

## Summary
Severity: High
Advisory: CVE-2025-57771
Aliases: GHSA-wrh9-463x-7wvv
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-08-22
Source: https://osv.dev/vulnerability/CVE-2025-57771
Type: osv

## Details
Roo Code is an AI-powered autonomous coding agent that lives in users' editors. In versions prior to 3.25.5, Roo-Code fails to properly handle process substitution and single ampersand characters in the command parsing logic for auto-execute commands. If a user has enabled auto-approved execution for a command such as ls, an attacker who can submit crafted prompts to the agent may inject arbitrary commands to be executed alongside the intended command. Exploitation requires attacker access to submit prompts and for the user to have enabled auto-approved command execution, which is disabled by default. This vulnerability could allow an attacker to execute arbitrary code. The issue is fixed in version 3.25.5.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/57xxx/CVE-2025-57771.json
- https://github.com/RooCodeInc/Roo-Code/security/advisories/GHSA-wrh9-463x-7wvv
- https://nvd.nist.gov/vuln/detail/CVE-2025-57771
- https://github.com/RooCodeInc/Roo-Code/commit/de359a465c67aefc67553aa2b464591b602c4bdc
