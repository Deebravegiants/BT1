# [H] [Eclipse Theia] Arbitrary Command Execution via Untrusted Workspace Task Definitions

## Summary
Severity: High
Advisory: GHSA-g9jw-92q7-g7fj
CVE: CVE-2026-44691
CWE: CWE-829
Ecosystem: npm
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-g9jw-92q7-g7fj
Type: github-advisory

## Affected
- npm: `@theia/debug` — affected >=0 <1.69.0
- npm: `@theia/task` — affected >=0 <1.69.0
- npm: `@theia/workspace` — affected >=0 <1.69.0

## Details
In Eclipse Theia versions prior to 1.69.0, custom task definitions in workspace files (e.g. .theia/tasks.json, .vscode/tasks.json) could be executed without requiring workspace trust. An attacker could craft a malicious repository that, when cloned and opened in Theia, leads to execution of arbitrary commands with the user's privileges. In combination with AI chat features and a workspace .theia/settings.json that disabled tool confirmation, this could be triggered automatically by sending a message in the AI chat.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-44691
- https://github.com/eclipse-theia/theia/issues/16889
- https://github.com/eclipse-theia/theia/pull/16917
- https://github.com/eclipse-theia/theia
- https://gitlab.eclipse.org/security/cve-assignment/-/work_items/116
- https://gitlab.eclipse.org/security/vulnerability-reports/-/work_items/331
