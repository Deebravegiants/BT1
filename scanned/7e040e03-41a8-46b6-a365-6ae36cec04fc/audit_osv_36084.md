# [C] CVE-2026-19884

## Summary
Severity: Critical
Advisory: CVE-2026-19884
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-14
Source: https://osv.dev/vulnerability/CVE-2026-19884
Type: osv

## Details
In Eclipse Theia versions up to and including 1.69.0, opening a folder starts source control integration without requiring the user to trust the folder first. This affects applications built on Theia that include the git integration, such as the Theia IDE. Both Theia's own `@theia/git` extension and the builtin VS Code `git` extension run git commands such as `git status` as soon as a repository is detected. Since git honors repository-local configuration, a folder containing an attacker-controlled `.git/config` with `core.fsmonitor` (or a comparable hook-like setting) causes the configured command to be executed. The configuration can be delivered by burying a bare repository inside a regular repository (OVE-20210718-0001), so cloning an attacker-supplied repository and opening it in a Theia-based application is sufficient to execute arbitrary commands with the privileges of the user, without any confirmation prompt.



As of 1.70.0, plugins that declare `capabilities.untrustedWorkspaces.supported: false`, which includes the builtin git extension, are no longer loaded or activated in an untrusted workspace, and the deprecated `@theia/git` extension has been removed, so no git command is executed against an untrusted folder.

## References
- https://gitlab.eclipse.org/security/cve-assignment/-/work_items/231
- https://gitlab.eclipse.org/security/vulnerability-reports/-/work_items/175
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/19xxx/CVE-2026-19884.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-19884
- https://github.com/eclipse-theia/theia/pull/16809
- https://github.com/eclipse-theia/theia/pull/17098
- https://github.com/eclipse-theia/theia/pull/17148
