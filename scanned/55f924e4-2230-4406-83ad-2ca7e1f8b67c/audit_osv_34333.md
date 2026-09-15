# [M] Roo Code: Symlink-bypass of .rooignore can lead to unintended file disclosure

## Summary
Severity: Medium
Advisory: CVE-2025-58373
Aliases: GHSA-p76r-7mc3-qh7c
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2025-09-05
Source: https://osv.dev/vulnerability/CVE-2025-58373
Type: osv

## Details
Roo Code is an AI-powered autonomous coding agent that lives in users' editors. Versions 3.25.23 and below contain a vulnerability where .rooignore protections could be bypassed using symlinks. This allows an attacker with write access to the workspace to trick the extension into reading files that were intended to be excluded. As a result, sensitive files such as .env or configuration files could be exposed. An attacker able to modify files within the workspace could gain unauthorized access to sensitive information by bypassing .rooignore rules. This could include secrets, configuration details, or other excluded project data. This is fixed in version 3.26.0.

## References
- https://github.com/RooCodeInc/Roo-Code/releases/tag/v3.26.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/58xxx/CVE-2025-58373.json
- https://github.com/RooCodeInc/Roo-Code/security/advisories/GHSA-p76r-7mc3-qh7c
- https://nvd.nist.gov/vuln/detail/CVE-2025-58373
- https://github.com/RooCodeInc/Roo-Code/pull/7405
