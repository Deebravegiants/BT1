# [H] mlxsw: spectrum_acl_tcam: Fix warning during rehash

## Summary
Severity: High
Advisory: CVE-2024-36007
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-20
Source: https://osv.dev/vulnerability/CVE-2024-36007
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.1.0 <5.4.275, >=5.5.0 <5.10.216, >=5.11.0 <5.15.158, >=5.16.0 <6.1.90, >=6.2.0 <6.6.30, >=6.7.0 <6.8.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

mlxsw: spectrum_acl_tcam: Fix warning during rehash

As previously explained, the rehash delayed work migrates filters from
one region to another. This is done by iterating over all chunks (all
the filters with the same priority) in the region and in each chunk
iterating over all the filters.

When the work runs out of credits it stores the current chunk and entry
as markers in the per-work context so that it would know where to resume
the migration from the next time the work is scheduled.

Upon error, the chunk marker is reset to NULL, but without resetting the
entry markers despite being relative to it. This can result in migration
being resumed from an entry that does not belong to the chunk being
migrated. In turn, this will eventually lead to a chunk being iterated
over as if it is an entry. Because of how the two structures happen to
be defined, this does not lead to KASAN splats, but to warnings such as
[1].

Fix by creating a helper that resets all the markers and call it from
all the places the currently only reset the chunk marker. For good
measures also call it when starting a completely new rehash. Add a
warning to avoid future cases.

[1]
WARNING: CPU: 7 PID: 1076 at drivers/net/ethernet/mellanox/mlxsw/core_acl_flex_keys.c:407 mlxsw_afk_encode+0x242/0x2f0
Modules linked in:
CPU: 7 PID: 1076 Comm: kworker/7:24 Tainted: G        W          6.9.0-rc3-custom-00880-g29e61d91b77b #29
Hardware name: Mellanox Technologies Ltd. MSN3700/VMOD0005, BIOS 5.11 01/06/2019
Workqueue: mlxsw_core mlxsw_sp_acl_tcam_vregion_rehash_work
RIP: 0010:mlxsw_afk_encode+0x242/0x2f0
[...]
Call Trace:
 <TASK>
 mlxsw_sp_acl_atcam_entry_add+0xd9/0x3c0
 mlxsw_sp_acl_tcam_entry_create+0x5e/0xa0
 mlxsw_sp_acl_tcam_vchunk_migrate_all+0x109/0x290
 mlxsw_sp_acl_tcam_vregion_rehash_work+0x6c/0x470
 process_one_work+0x151/0x370
 worker_thread+0x2cb/0x3e0
 kthread+0xd0/0x100
 ret_from_fork+0x34/0x50
 </TASK>

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://cert-portal.siemens.com/productcert/html/ssa-613116.html
- https://git.kernel.org/stable/c/039992b6d2df097c65f480dcf269de3d2656f573
- https://git.kernel.org/stable/c/0b88631855026b55cad901ac28d081e0f358e596
- https://git.kernel.org/stable/c/17e9e0bbae652b9b2049e51699e93dfa60b2988d
- https://git.kernel.org/stable/c/1d76bd2a0034d0d08045c1c6adf2235d88982952
- https://git.kernel.org/stable/c/743edc8547a92b6192aa1f1b6bb78233fa21dc9b
- https://git.kernel.org/stable/c/751d352858108314efd33dddd5a9a2b6bf7d6916
- https://git.kernel.org/stable/c/e890456051fe8c57944b911defb3e6de91315861
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/36xxx/CVE-2024-36007.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-36007
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
