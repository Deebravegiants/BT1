# [H] vscode-spell-checker has a workspace-trust bypass Code Execution

## Summary
Severity: High
Advisory: CVE-2026-25931
Aliases: GHSA-mggq-68mr-58vj
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-02-09
Source: https://osv.dev/vulnerability/CVE-2026-25931
Type: osv

## Details
vscode-spell-checker is a basic spell checker that works well with code and documents. Prior to v4.5.4, DocumentSettings._determineIsTrusted treats the configuration value cSpell.trustedWorkspace as the authoritative trust flag. The value defaults to true (package.json) and is read from workspace configuration each time settings are fetched. The code coerces any truthy value to true and forwards it to ConfigLoader.setIsTrusted , which in turn allows JavaScript/TypeScript configuration files ( .cspell.config.js/.mjs/.ts , etc.) to be located and executed. Because no VS Code workspace-trust state is consulted, an untrusted workspace can keep the flag true and place a malicious .cspell.config.js ; opening the workspace causes the extension host to execute attacker-controlled Node.js code with the user’s privileges. This vulnerability is fixed in v4.5.4.

## References
- https://drive.google.com/file/d/1mT4SOkkHSHU6NFfKwekysydAd3FUAC6K/view?usp=sharing
- https://github.com/streetsidesoftware/vscode-spell-checker/releases/tag/code-spell-checker-v4.5.4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25931.json
- https://github.com/streetsidesoftware/vscode-spell-checker/security/advisories/GHSA-mggq-68mr-58vj
- https://nvd.nist.gov/vuln/detail/CVE-2026-25931
- https://github.com/streetsidesoftware/vscode-spell-checker/commit/f39af9a3a6f2a939a57171a24161ed735d41c575
