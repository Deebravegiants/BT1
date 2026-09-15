# [H] lib: objagg: Fix general protection fault

## Summary
Severity: High
Advisory: CVE-2024-43846
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-08-17
Source: https://osv.dev/vulnerability/CVE-2024-43846
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.1.0 <5.4.282, >=5.5.0 <5.10.224, >=5.11.0 <5.15.165, >=5.16.0 <6.1.103, >=6.2.0 <6.6.44, >=6.7.0 <6.10.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

lib: objagg: Fix general protection fault

The library supports aggregation of objects into other objects only if
the parent object does not have a parent itself. That is, nesting is not
supported.

Aggregation happens in two cases: Without and with hints, where hints
are a pre-computed recommendation on how to aggregate the provided
objects.

Nesting is not possible in the first case due to a check that prevents
it, but in the second case there is no check because the assumption is
that nesting cannot happen when creating objects based on hints. The
violation of this assumption leads to various warnings and eventually to
a general protection fault [1].

Before fixing the root cause, error out when nesting happens and warn.

[1]
general protection fault, probably for non-canonical address 0xdead000000000d90: 0000 [#1] PREEMPT SMP PTI
CPU: 1 PID: 1083 Comm: kworker/1:9 Tainted: G        W          6.9.0-rc6-custom-gd9b4f1cca7fb #7
Hardware name: Mellanox Technologies Ltd. MSN3700/VMOD0005, BIOS 5.11 01/06/2019
Workqueue: mlxsw_core mlxsw_sp_acl_tcam_vregion_rehash_work
RIP: 0010:mlxsw_sp_acl_erp_bf_insert+0x25/0x80
[...]
Call Trace:
 <TASK>
 mlxsw_sp_acl_atcam_entry_add+0x256/0x3c0
 mlxsw_sp_acl_tcam_entry_create+0x5e/0xa0
 mlxsw_sp_acl_tcam_vchunk_migrate_one+0x16b/0x270
 mlxsw_sp_acl_tcam_vregion_rehash_work+0xbe/0x510
 process_one_work+0x151/0x370
 worker_thread+0x2cb/0x3e0
 kthread+0xd0/0x100
 ret_from_fork+0x34/0x50
 ret_from_fork_asm+0x1a/0x30
 </TASK>

## References
- https://git.kernel.org/stable/c/1936fa05a180834c3b52e0439a6bddc07814d3eb
- https://git.kernel.org/stable/c/22ae17a267f4812861f0c644186c3421ff97dbfc
- https://git.kernel.org/stable/c/499f742fed42e74f1321f4b12ca196a66a2b49fc
- https://git.kernel.org/stable/c/565213e005557eb6cc4e42189d26eb300e02f170
- https://git.kernel.org/stable/c/5adc61d29bbb461d7f7c2b48dceaa90ecd182eb7
- https://git.kernel.org/stable/c/8161263362154cbebfbf4808097b956a6a8cb98a
- https://git.kernel.org/stable/c/b4a3a89fffcdf09702b1f161b914e52abca1894d
- https://lists.debian.org/debian-lts-announce/2024/10/msg00003.html
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/43xxx/CVE-2024-43846.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-43846
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
