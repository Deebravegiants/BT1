# [H] Roo Code allows Potential Remote Code Execution via .vscode/settings.json

## Summary
Severity: High
Advisory: CVE-2025-53536
Aliases: GHSA-3765-5vjr-qjgm
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-07
Source: https://osv.dev/vulnerability/CVE-2025-53536
Type: osv

## Details
Roo Code is an AI-powered autonomous coding agent. Prior to 3.22.6, if the victim had "Write" auto-approved, an attacker with the ability to submit prompts to the agent could write to VS Code settings files and trigger code execution. There were multiple ways to achieve that. One example is with the php.validate.executablePath setting which lets you set the path for the php executable for syntax validation. The attacker could have written the path to an arbitrary command there and then created a php file to trigger it. This vulnerability is fixed in 3.22.6.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/53xxx/CVE-2025-53536.json
- https://github.com/RooCodeInc/Roo-Code/security/advisories/GHSA-3765-5vjr-qjgm
- https://nvd.nist.gov/vuln/detail/CVE-2025-53536
- https://github.com/RooCodeInc/Roo-Code/commit/1be6fce1a6864ae63e8160b0666db2c647f2dbba
- https://github.com/RooCodeInc/Roo-Code/commit/3993406ebdc0553a32ef391a799a4fb124930a1c
