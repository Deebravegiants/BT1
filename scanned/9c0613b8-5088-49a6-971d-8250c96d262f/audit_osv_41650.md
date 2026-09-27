# [C] Incus: Cross-project instance copy bypasses target project restrictions via TOCTOU in config merge

## Summary
Severity: Critical
Advisory: CVE-2026-62941
Aliases: GHSA-mq9x-prm8-3vpw
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-21
Source: https://osv.dev/vulnerability/CVE-2026-62941
Type: osv

## Details
Incus is a system container and virtual machine manager. Prior to version 7.3.0, when copying an instance across projects, the project restriction check (`AllowInstanceCreation`) runs BEFORE the source instance's configuration is merged into the request. Dangerous configuration keys (including `security.privileged`, `raw.lxc`, `raw.apparmor`) from the source instance are merged AFTER the check passes, bypassing all project restrictions on the target project. Version 7.3.0 patches the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/62xxx/CVE-2026-62941.json
- https://github.com/lxc/incus/security/advisories/GHSA-mq9x-prm8-3vpw
- https://nvd.nist.gov/vuln/detail/CVE-2026-62941
