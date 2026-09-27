# [H] NFS: Fix potential buffer overflowin nfs_sysfs_link_rpc_client()

## Summary
Severity: High
Advisory: CVE-2024-54456
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-27
Source: https://osv.dev/vulnerability/CVE-2024-54456
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.5.0 <6.6.79, >=6.7.0 <6.12.16, >=6.13.0 <6.13.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

NFS: Fix potential buffer overflowin nfs_sysfs_link_rpc_client()

name is char[64] where the size of clnt->cl_program->name remains
unknown. Invoking strcat() directly will also lead to potential buffer
overflow. Change them to strscpy() and strncat() to fix potential
issues.

## References
- https://git.kernel.org/stable/c/19b3ca651b4b473878c73539febe477905041442
- https://git.kernel.org/stable/c/49fd4e34751e90e6df009b70cd0659dc839e7ca8
- https://git.kernel.org/stable/c/dd8830779b77f4d1206d28d02ad56a03fc0e78f7
- https://git.kernel.org/stable/c/e8e0eb5601d4a6c74c336e3710afe3a0348c469d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/54xxx/CVE-2024-54456.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-54456
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
