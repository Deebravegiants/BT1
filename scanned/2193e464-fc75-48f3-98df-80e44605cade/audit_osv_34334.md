# [H] Roo Code: Auto-approve allows npm install execution of malicious postinstall scripts

## Summary
Severity: High
Advisory: CVE-2025-58374
Aliases: GHSA-c292-qxq4-4p2v
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-09-06
Source: https://osv.dev/vulnerability/CVE-2025-58374
Type: osv

## Details
Roo Code is an AI-powered autonomous coding agent that lives in users' editors. Versions 3.25.23 and below contain a default list of allowed commands that do not need manual approval if auto-approve is enabled, and npm install is included in that list. Because npm install executes lifecycle scripts, if a repository’s package.json file contains a malicious postinstall script, it would be executed automatically without user approval. This means that enabling auto-approved commands and opening a malicious repo could result in arbitrary code execution. This is fixed in version 3.26.0.

## References
- https://github.com/RooCodeInc/Roo-Code/pull/7390/files
- https://github.com/RooCodeInc/Roo-Code/releases/tag/v3.26.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/58xxx/CVE-2025-58374.json
- https://github.com/RooCodeInc/Roo-Code/security/advisories/GHSA-c292-qxq4-4p2v
- https://nvd.nist.gov/vuln/detail/CVE-2025-58374
