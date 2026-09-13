# [M] Incus: Project restriction `restricted.containers.privilege=isolated` bypassable by omitting `security.idmap.isolated`

## Summary
Severity: Medium
Advisory: CVE-2026-62313
Aliases: GHSA-53cg-qvg7-m8vg
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-08-21
Source: https://osv.dev/vulnerability/CVE-2026-62313
Type: osv

## Details
Incus is a system container and virtual machine manager. Prior to version 7.3.0, project-level enforcement of `restricted.containers.privilege=isolated` can be trivially bypassed, allowing a user to create a non-isolated (shared host idmap) container in a project that is configured to forbid them. The restriction only rejects an explicitly set `security.idmap.isolated=false` (or empty) and fails to enforce anything when the key is omitted entirely. Because an unset `security.idmap.isolated` defaults to `false` (non-isolation), a user simply leaves the key out and obtains exactly the container state the restriction is meant to forbid. This defeats the tenant-isolation guarantee the restriction exists to provide. Containers in the project share the host uid/gid map instead of receiving unique, non-overlapping ranges, weakening the isolation boundary between co-tenant containers and the host. Version 7.3.0 patches the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/62xxx/CVE-2026-62313.json
- https://github.com/lxc/incus/security/advisories/GHSA-53cg-qvg7-m8vg
- https://nvd.nist.gov/vuln/detail/CVE-2026-62313
