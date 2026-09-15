# [H] net: fix UAF issue in nfqnl_nf_hook_drop() when ops_init() failed

## Summary
Severity: High
Advisory: CVE-2022-50780
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-24
Source: https://osv.dev/vulnerability/CVE-2022-50780
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.33 <4.19.264, >=4.20.0 <5.4.223, >=5.5.0 <5.10.153, >=5.11.0 <5.15.77, >=5.16.0 <6.0.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: fix UAF issue in nfqnl_nf_hook_drop() when ops_init() failed

When the ops_init() interface is invoked to initialize the net, but
ops->init() fails, data is released. However, the ptr pointer in
net->gen is invalid. In this case, when nfqnl_nf_hook_drop() is invoked
to release the net, invalid address access occurs.

The process is as follows:
setup_net()
	ops_init()
		data = kzalloc(...)   ---> alloc "data"
		net_assign_generic()  ---> assign "date" to ptr in net->gen
		...
		ops->init()           ---> failed
		...
		kfree(data);          ---> ptr in net->gen is invalid
	...
	ops_exit_list()
		...
		nfqnl_nf_hook_drop()
			*q = nfnl_queue_pernet(net) ---> q is invalid

The following is the Call Trace information:
BUG: KASAN: use-after-free in nfqnl_nf_hook_drop+0x264/0x280
Read of size 8 at addr ffff88810396b240 by task ip/15855
Call Trace:
<TASK>
dump_stack_lvl+0x8e/0xd1
print_report+0x155/0x454
kasan_report+0xba/0x1f0
nfqnl_nf_hook_drop+0x264/0x280
nf_queue_nf_hook_drop+0x8b/0x1b0
__nf_unregister_net_hook+0x1ae/0x5a0
nf_unregister_net_hooks+0xde/0x130
ops_exit_list+0xb0/0x170
setup_net+0x7ac/0xbd0
copy_net_ns+0x2e6/0x6b0
create_new_namespaces+0x382/0xa50
unshare_nsproxy_namespaces+0xa6/0x1c0
ksys_unshare+0x3a4/0x7e0
__x64_sys_unshare+0x2d/0x40
do_syscall_64+0x35/0x80
entry_SYSCALL_64_after_hwframe+0x46/0xb0
</TASK>

Allocated by task 15855:
kasan_save_stack+0x1e/0x40
kasan_set_track+0x21/0x30
__kasan_kmalloc+0xa1/0xb0
__kmalloc+0x49/0xb0
ops_init+0xe7/0x410
setup_net+0x5aa/0xbd0
copy_net_ns+0x2e6/0x6b0
create_new_namespaces+0x382/0xa50
unshare_nsproxy_namespaces+0xa6/0x1c0
ksys_unshare+0x3a4/0x7e0
__x64_sys_unshare+0x2d/0x40
do_syscall_64+0x35/0x80
entry_SYSCALL_64_after_hwframe+0x46/0xb0

Freed by task 15855:
kasan_save_stack+0x1e/0x40
kasan_set_track+0x21/0x30
kasan_save_free_info+0x2a/0x40
____kasan_slab_free+0x155/0x1b0
slab_free_freelist_hook+0x11b/0x220
__kmem_cache_free+0xa4/0x360
ops_init+0xb9/0x410
setup_net+0x5aa/0xbd0
copy_net_ns+0x2e6/0x6b0
create_new_namespaces+0x382/0xa50
unshare_nsproxy_namespaces+0xa6/0x1c0
ksys_unshare+0x3a4/0x7e0
__x64_sys_unshare+0x2d/0x40
do_syscall_64+0x35/0x80
entry_SYSCALL_64_after_hwframe+0x46/0xb0

## References
- https://git.kernel.org/stable/c/4a4df5e78712de39d6f90d6a64b5eb48dca03bd5
- https://git.kernel.org/stable/c/5a2ea549be94924364f6911227d99be86e8cf34a
- https://git.kernel.org/stable/c/97ad240fd9aa9214497d14af2b91608e20856cac
- https://git.kernel.org/stable/c/a1e18acb0246bfb001b08b8b1b830b5ec92a0f13
- https://git.kernel.org/stable/c/c3edc6e808209aa705185f732e682a370981ced1
- https://git.kernel.org/stable/c/d266935ac43d57586e311a087510fe6a084af742
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50780.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50780
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
