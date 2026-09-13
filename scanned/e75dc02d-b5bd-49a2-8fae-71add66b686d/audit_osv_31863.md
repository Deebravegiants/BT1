# [H] NFSv4: Fix a deadlock when recovering state on a sillyrenamed file

## Summary
Severity: High
Advisory: CVE-2025-21900
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-04-01
Source: https://osv.dev/vulnerability/CVE-2025-21900
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.12.18, >=6.13.0 <6.13.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

NFSv4: Fix a deadlock when recovering state on a sillyrenamed file

If the file is sillyrenamed, and slated for delete on close, it is
possible for a server reboot to triggeer an open reclaim, with can again
race with the application call to close(). When that happens, the call
to put_nfs_open_context() can trigger a synchronous delegreturn call
which deadlocks because it is not marked as privileged.

Instead, ensure that the call to nfs4_inode_return_delegation_on_close()
catches the delegreturn, and schedules it asynchronously.

## References
- https://git.kernel.org/stable/c/4fe4ae6c2e01d028856b73b6328b12b8945df871
- https://git.kernel.org/stable/c/8f8df955f078e1a023ee55161935000a67651f38
- https://git.kernel.org/stable/c/f41a60bc43e7abbc636fee78bed0d74c31e738b0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21900.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21900
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
