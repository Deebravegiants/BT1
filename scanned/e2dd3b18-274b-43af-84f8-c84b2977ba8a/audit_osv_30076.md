# [H] ocfs2: cancel dqi_sync_work before freeing oinfo

## Summary
Severity: High
Advisory: CVE-2024-49966
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2024-49966
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.29 <4.19.323, >=4.20.0 <5.4.285, >=5.5.0 <5.10.227, >=5.11.0 <5.15.168, >=5.16.0 <6.1.113, >=6.2.0 <6.6.55, >=6.7.0 <6.10.14, >=6.11.0 <6.11.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

ocfs2: cancel dqi_sync_work before freeing oinfo

ocfs2_global_read_info() will initialize and schedule dqi_sync_work at the
end, if error occurs after successfully reading global quota, it will
trigger the following warning with CONFIG_DEBUG_OBJECTS_* enabled:

ODEBUG: free active (active state 0) object: 00000000d8b0ce28 object type: timer_list hint: qsync_work_fn+0x0/0x16c

This reports that there is an active delayed work when freeing oinfo in
error handling, so cancel dqi_sync_work first.  BTW, return status instead
of -1 when .read_file_info fails.

## References
- https://git.kernel.org/stable/c/0d707a33c84b371cb66120e198eed3374726ddd8
- https://git.kernel.org/stable/c/14114d8148db07e7946fb06b56a50cfa425e26c7
- https://git.kernel.org/stable/c/35fccce29feb3706f649726d410122dd81b92c18
- https://git.kernel.org/stable/c/4173d1277c00baeedaaca76783e98b8fd0e3c08d
- https://git.kernel.org/stable/c/89043e7ed63c7fc141e68ea5a79758ed24b6c699
- https://git.kernel.org/stable/c/a4346c04d055bf7e184c18a73dbd23b6a9811118
- https://git.kernel.org/stable/c/bbf41277df8b33fbedf4750a9300c147e8f104eb
- https://git.kernel.org/stable/c/ef768020366f47d23f39c4f57bcb03af6d1e24b3
- https://git.kernel.org/stable/c/fc5cc716dfbdc5fd5f373ff3b51358174cf88bfc
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/49xxx/CVE-2024-49966.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-49966
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
