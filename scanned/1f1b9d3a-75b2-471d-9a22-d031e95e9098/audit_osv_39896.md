# [C] Workspace settings can override executable and Gemfile paths used by the Ruby LSP VS Code extension

## Summary
Severity: Critical
Advisory: CVE-2026-48122
Aliases: GHSA-2x7g-8mp4-572w
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:L/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-07
Source: https://osv.dev/vulnerability/CVE-2026-48122
Type: osv

## Details
Ruby LSP is an implementation of the language server protocol for Ruby. Several workspace-level settings in the Ruby LSP VS Code extension prior to version 0.10.4 could override the path to the Ruby executable, the version manager executables, or the Bundler `Gemfile` used at startup. A malicious repository containing a `.vscode/settings.json` could set these values to attacker-controlled targets. Opening and trusting the repository would then execute code with the privileges of the developer. The Ruby LSP gem and clients of the language server in other editors are not affected. Version 0.10.4 of the Ruby LSP VS Code extension fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48122.json
- https://github.com/Shopify/ruby-lsp/security/advisories/GHSA-2x7g-8mp4-572w
- https://nvd.nist.gov/vuln/detail/CVE-2026-48122
