# [H] Roo Code is Vulnerable to Potential Remote Code Execution via zsh Command Validation Bug

## Summary
Severity: High
Advisory: CVE-2025-65946
Aliases: GHSA-hwm7-w97p-4h8p
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-11-21
Source: https://osv.dev/vulnerability/CVE-2025-65946
Type: osv

## Details
Roo Code is an AI-powered autonomous coding agent that lives in users' editors. Prior to version 3.26.7, Due to an error in validation it was possible for Roo to automatically execute commands that did not match the allow list prefixes. This issue has been patched in version 3.26.7.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/65xxx/CVE-2025-65946.json
- https://github.com/RooCodeInc/Roo-Code/security/advisories/GHSA-hwm7-w97p-4h8p
- https://nvd.nist.gov/vuln/detail/CVE-2025-65946
- https://github.com/RooCodeInc/Roo-Code/commit/b50104cc5987ce64f5154309d967ae8c74cfd1f3
- https://github.com/RooCodeInc/Roo-Code/pull/7667
