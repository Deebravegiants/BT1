# [H] mlxsw: spectrum_acl_tcam: Fix stack corruption

## Summary
Severity: High
Advisory: CVE-2024-26586
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-02-22
Source: https://osv.dev/vulnerability/CVE-2024-26586
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.19.0 <5.10.209, >=5.11.0 <5.15.148, >=5.16.0 <6.1.79, >=6.2.0 <6.6.14, >=6.7.0 <6.7.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

mlxsw: spectrum_acl_tcam: Fix stack corruption

When tc filters are first added to a net device, the corresponding local
port gets bound to an ACL group in the device. The group contains a list
of ACLs. In turn, each ACL points to a different TCAM region where the
filters are stored. During forwarding, the ACLs are sequentially
evaluated until a match is found.

One reason to place filters in different regions is when they are added
with decreasing priorities and in an alternating order so that two
consecutive filters can never fit in the same region because of their
key usage.

In Spectrum-2 and newer ASICs the firmware started to report that the
maximum number of ACLs in a group is more than 16, but the layout of the
register that configures ACL groups (PAGT) was not updated to account
for that. It is therefore possible to hit stack corruption [1] in the
rare case where more than 16 ACLs in a group are required.

Fix by limiting the maximum ACL group size to the minimum between what
the firmware reports and the maximum ACLs that fit in the PAGT register.

Add a test case to make sure the machine does not crash when this
condition is hit.

[1]
Kernel panic - not syncing: stack-protector: Kernel stack is corrupted in: mlxsw_sp_acl_tcam_group_update+0x116/0x120
[...]
 dump_stack_lvl+0x36/0x50
 panic+0x305/0x330
 __stack_chk_fail+0x15/0x20
 mlxsw_sp_acl_tcam_group_update+0x116/0x120
 mlxsw_sp_acl_tcam_group_region_attach+0x69/0x110
 mlxsw_sp_acl_tcam_vchunk_get+0x492/0xa20
 mlxsw_sp_acl_tcam_ventry_add+0x25/0xe0
 mlxsw_sp_acl_rule_add+0x47/0x240
 mlxsw_sp_flower_replace+0x1a9/0x1d0
 tc_setup_cb_add+0xdc/0x1c0
 fl_hw_replace_filter+0x146/0x1f0
 fl_change+0xc17/0x1360
 tc_new_tfilter+0x472/0xb90
 rtnetlink_rcv_msg+0x313/0x3b0
 netlink_rcv_skb+0x58/0x100
 netlink_unicast+0x244/0x390
 netlink_sendmsg+0x1e4/0x440
 ____sys_sendmsg+0x164/0x260
 ___sys_sendmsg+0x9a/0xe0
 __sys_sendmsg+0x7a/0xc0
 do_syscall_64+0x40/0xe0
 entry_SYSCALL_64_after_hwframe+0x63/0x6b

## References
- https://git.kernel.org/stable/c/2f5e1565740490706332c06f36211d4ce0f88e62
- https://git.kernel.org/stable/c/348112522a35527c5bcba933b9fefb40a4f44f15
- https://git.kernel.org/stable/c/483ae90d8f976f8339cf81066312e1329f2d3706
- https://git.kernel.org/stable/c/56750ea5d15426b5f307554e7699e8b5f76c3182
- https://git.kernel.org/stable/c/6fd24675188d354b1cad47462969afa2ab09d819
- https://git.kernel.org/stable/c/a361c2c1da5dbb13ca67601cf961ab3ad68af383
- https://lists.debian.org/debian-lts-announce/2024/06/msg00016.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26586.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26586
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
