# [C] knowns before 0.30.0 Arbitrary Code Execution via LSP Binary

## Summary
Severity: Critical
Advisory: CVE-2026-86540
Aliases: GHSA-mc52-mwq4-vfx3
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-07
Source: https://osv.dev/vulnerability/CVE-2026-86540
Type: osv

## Details
knowns versions before 0.30.0 fail to validate the settings.lsp.languages binary field in project configuration files, allowing attackers to execute arbitrary binaries by crafting a malicious .knowns/config.json file. When a repository with a crafted configuration is opened, the unvalidated binary path is executed twice under the user's account without any verification.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/86xxx/CVE-2026-86540.json
- https://github.com/knowns-dev/knowns/releases/tag/v0.30.0
- https://github.com/knowns-dev/knowns/security/advisories/GHSA-mc52-mwq4-vfx3
- https://nvd.nist.gov/vuln/detail/CVE-2026-86540
- https://www.vulncheck.com/advisories/knowns-before-0.30.0-arbitrary-code-execution-via-lsp-binary
- https://github.com/knowns-dev/knowns/commit/d3989829fb5095666d23d005b2f78a082832a396
- https://github.com/knowns-dev/knowns/blob/v0.29.1/internal/lsp/detect.go#L128-L157
- https://github.com/knowns-dev/knowns/blob/v0.29.1/internal/models/config.go#L205-L216
