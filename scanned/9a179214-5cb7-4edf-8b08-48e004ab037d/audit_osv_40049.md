# [H] CodexBar < 0.32.0 Insecure Temporary File Handling in Notarization Workflow

## Summary
Severity: High
Advisory: CVE-2026-49135
CVSS: 7.5 (CVSS:4.0/AV:L/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-01
Source: https://osv.dev/vulnerability/CVE-2026-49135
Type: osv

## Details
CodexBar prior to 0.32.0 contains an insecure temporary file handling vulnerability that allows local attackers to access sensitive credentials or tamper with build artifacts by exploiting predictable file paths in the release notarization workflow. Attackers with access to the same host can read the App Store Connect API key written to a fixed path, pre-create files or symbolic links at predictable locations to redirect writes to attacker-controlled destinations, or tamper with notarization archives before submission.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/49xxx/CVE-2026-49135.json
- https://github.com/steipete/CodexBar/releases/tag/v0.32.0
- https://nvd.nist.gov/vuln/detail/CVE-2026-49135
- https://www.vulncheck.com/advisories/codexbar-insecure-temporary-file-handling-in-notarization-workflow
- https://github.com/steipete/CodexBar/pull/1228
- https://github.com/steipete/CodexBar/commit/e7d932616508cee43ea9bcc63c269b14698de655
- https://github.com/steipete/CodexBar
