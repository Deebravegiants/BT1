# [H] Claude Code Vulnerable to Arbitrary Code Execution via Plugin Autoloading with Specific Yarn Versions

## Summary
Severity: High
Advisory: GHSA-2jjv-qf24-vfm4
CVE: CVE-2025-59828
CWE: CWE-829, CWE-862
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-09-24
Source: https://github.com/advisories/GHSA-2jjv-qf24-vfm4
Type: github-advisory

## Affected
- npm: `@anthropic-ai/claude-code` — affected >=0 <1.0.39

## Details
When using Claude Code with Yarn installed, Yarn config files can trigger code execution when running `yarn --version`. This could lead to a bypass of the directory trust dialog in Claude Code, as plugins and `yarnPath` could be executed prior to the user accepting the risks of working in an untrusted directory. Users on standard Claude Code auto-update will have received this fix automatically. Users performing manual updates are advised to update to the latest version.

Thank you to Benjamin Faller, Redguard AG and Michael Hess for reporting this issue!

## References
- https://github.com/anthropics/claude-code/security/advisories/GHSA-2jjv-qf24-vfm4
- https://nvd.nist.gov/vuln/detail/CVE-2025-59828
- https://github.com/anthropics/claude-code
- https://osv.dev/vulnerability/GHSA-2jjv-qf24-vfm4
- https://www.cve.org/CVERecord?id=CVE-2025-59828
- https://yarnpkg.com/advanced/plugin-tutorial
