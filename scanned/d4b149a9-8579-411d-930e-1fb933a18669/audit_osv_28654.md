# [M] mlxsw: spectrum_acl_tcam: Fix memory leak during rehash

## Summary
Severity: Medium
Advisory: CVE-2024-35853
Ecosystem: Linux
CVSS: 6.4 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:H)
Published: 2024-05-17
Source: https://osv.dev/vulnerability/CVE-2024-35853
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.1.0 <5.4.275, >=5.5.0 <5.10.216, >=5.11.0 <5.15.158, >=5.16.0 <6.1.90, >=6.2.0 <6.6.30, >=6.7.0 <6.8.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

mlxsw: spectrum_acl_tcam: Fix memory leak during rehash

The rehash delayed work migrates filters from one region to another.
This is done by iterating over all chunks (all the filters with the same
priority) in the region and in each chunk iterating over all the
filters.

If the migration fails, the code tries to migrate the filters back to
the old region. However, the rollback itself can also fail in which case
another migration will be erroneously performed. Besides the fact that
this ping pong is not a very good idea, it also creates a problem.

Each virtual chunk references two chunks: The currently used one
('vchunk->chunk') and a backup ('vchunk->chunk2'). During migration the
first holds the chunk we want to migrate filters to and the second holds
the chunk we are migrating filters from.

The code currently assumes - but does not verify - that the backup chunk
does not exist (NULL) if the currently used chunk does not reference the
target region. This assumption breaks when we are trying to rollback a
rollback, resulting in the backup chunk being overwritten and leaked
[1].

Fix by not rolling back a failed rollback and add a warning to avoid
future cases.

[1]
WARNING: CPU: 5 PID: 1063 at lib/parman.c:291 parman_destroy+0x17/0x20
Modules linked in:
CPU: 5 PID: 1063 Comm: kworker/5:11 Tainted: G        W          6.9.0-rc2-custom-00784-gc6a05c468a0b #14
Hardware name: Mellanox Technologies Ltd. MSN3700/VMOD0005, BIOS 5.11 01/06/2019
Workqueue: mlxsw_core mlxsw_sp_acl_tcam_vregion_rehash_work
RIP: 0010:parman_destroy+0x17/0x20
[...]
Call Trace:
 <TASK>
 mlxsw_sp_acl_atcam_region_fini+0x19/0x60
 mlxsw_sp_acl_tcam_region_destroy+0x49/0xf0
 mlxsw_sp_acl_tcam_vregion_rehash_work+0x1f1/0x470
 process_one_work+0x151/0x370
 worker_thread+0x2cb/0x3e0
 kthread+0xd0/0x100
 ret_from_fork+0x34/0x50
 ret_from_fork_asm+0x1a/0x30
 </TASK>

## References
- https://git.kernel.org/stable/c/0ae8ff7b6d42e33943af462910bdcfa2ec0cb8cf
- https://git.kernel.org/stable/c/413a01886c3958d4b8aac23a3bff3d430b92093e
- https://git.kernel.org/stable/c/617e98ba4c50f4547c9eb0946b1cfc26937d70d1
- https://git.kernel.org/stable/c/8ca3f7a7b61393804c46f170743c3b839df13977
- https://git.kernel.org/stable/c/b3fd51f684a0711504f82de510da109ae639722d
- https://git.kernel.org/stable/c/b822644fd90992ee362c5e0c8d2556efc8856c76
- https://git.kernel.org/stable/c/c6f3fa7f5a748bf6e5c4eb742686d6952f854e76
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35853.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-35853
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
