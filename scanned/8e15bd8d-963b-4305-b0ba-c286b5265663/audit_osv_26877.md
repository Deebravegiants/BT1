# [C] cifs: fix potential race when tree connecting ipc

## Summary
Severity: Critical
Advisory: CVE-2023-54280
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-30
Source: https://osv.dev/vulnerability/CVE-2023-54280
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.16.0 <6.2.15, >=6.3.0 <6.3.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

cifs: fix potential race when tree connecting ipc

Protect access of TCP_Server_Info::hostname when building the ipc tree
name as it might get freed in cifsd thread and thus causing an
use-after-free bug in __tree_connect_dfs_target().  Also, while at it,
update status of IPC tcon on success and then avoid any extra tree
connects.

## References
- https://git.kernel.org/stable/c/536ec71ba060a02fabe8e22cecb82fe7b3a8708b
- https://git.kernel.org/stable/c/553476df55a111e6a66ad9155256aec0ec1b7ad0
- https://git.kernel.org/stable/c/ee20d7c6100752eaf2409d783f4f1449c29ea33d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/54xxx/CVE-2023-54280.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-54280
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
