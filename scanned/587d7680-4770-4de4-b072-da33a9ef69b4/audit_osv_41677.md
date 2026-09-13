# [C] Incus vulnerable to root RCE via image backup.yaml symlink

## Summary
Severity: Critical
Advisory: CVE-2026-63125
Aliases: GHSA-6rqx-22hc-qm36
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-21
Source: https://osv.dev/vulnerability/CVE-2026-63125
Type: osv

## Details
Incus is a system container and virtual machine manager. Prior to version 7.3.0, an unprivileged, project-confined Incus user (a non-admin TLS/RBAC identity with `can_create_images` and `can_create_instances`) can execute arbitrary code as root on the host. A crafted image ships `backup.yaml` as a symlink to a host file. When the root daemon writes the instance's backup file, it follows the symlink. Version 7.3.0 patches the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63125.json
- https://github.com/lxc/incus/security/advisories/GHSA-6rqx-22hc-qm36
- https://nvd.nist.gov/vuln/detail/CVE-2026-63125
