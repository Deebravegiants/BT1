# [C] Incus has a project restriction bypass via instance migration config override

## Summary
Severity: Critical
Advisory: CVE-2026-62940
Aliases: GHSA-qw5c-v953-38gw
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-21
Source: https://osv.dev/vulnerability/CVE-2026-62940
Type: osv

## Details
Incus is a system container and virtual machine manager. Prior to version 7.3.0, when migrating an instance to another cluster member, user-supplied configuration overrides (including security-critical keys like `security.privileged` and `raw.lxc`) are applied without any project restriction enforcement, allowing a restricted project user to escalate to a privileged container and escape to the host. Version 7.3.0 patches the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/62xxx/CVE-2026-62940.json
- https://github.com/lxc/incus/security/advisories/GHSA-qw5c-v953-38gw
- https://nvd.nist.gov/vuln/detail/CVE-2026-62940
