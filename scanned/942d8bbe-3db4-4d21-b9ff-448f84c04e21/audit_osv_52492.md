# [M] CVE-2021-47507

## Summary
Severity: Medium
Advisory: CVE-2021-47507
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-24
Source: https://osv.dev/vulnerability/CVE-2021-47507
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

nfsd: Fix nsfd startup race (again)

Commit bd5ae9288d64 ("nfsd: register pernet ops last, unregister first")
has re-opened rpc_pipefs_event() race against nfsd_net_id registration
(register_pernet_subsys()) which has been fixed by commit bb7ffbf29e76
("nfsd: fix nsfd startup race triggering BUG_ON").

Restore the order of register_pernet_subsys() vs register_cld_notifier().
Add WARN_ON() to prevent a future regression.

Crash info:
Unable to handle kernel NULL pointer dereference at virtual address 0000000000000012
CPU: 8 PID: 345 Comm: mount Not tainted 5.4.144-... #1
pc : rpc_pipefs_event+0x54/0x120 [nfsd]
lr : rpc_pipefs_event+0x48/0x120 [nfsd]
Call trace:
 rpc_pipefs_event+0x54/0x120 [nfsd]
 blocking_notifier_call_chain
 rpc_fill_super
 get_tree_keyed
 rpc_fs_get_tree
 vfs_get_tree
 do_mount
 ksys_mount
 __arm64_sys_mount
 el0_svc_handler
 el0_svc

## References
- https://git.kernel.org/stable/c/8bf902fee5893cfc2f04a698abab47629699ae9a
- https://git.kernel.org/stable/c/b10252c7ae9c9d7c90552f88b544a44ee773af64
- https://git.kernel.org/stable/c/c520943a00ad5015704969ad3304c956bcd49d25
- https://git.kernel.org/stable/c/f5734b1714ca355703e9ea8fb61d04beff1790b9
