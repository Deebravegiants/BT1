# [H] netfilter: Fix use-after-free in get_info()

## Summary
Severity: High
Advisory: CVE-2024-50257
Ecosystem: Linux
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-09
Source: https://osv.dev/vulnerability/CVE-2024-50257
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.171, >=5.16.0 <6.1.116, >=6.2.0 <6.6.60, >=6.7.0 <6.11.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: Fix use-after-free in get_info()

ip6table_nat module unload has refcnt warning for UAF. call trace is:

WARNING: CPU: 1 PID: 379 at kernel/module/main.c:853 module_put+0x6f/0x80
Modules linked in: ip6table_nat(-)
CPU: 1 UID: 0 PID: 379 Comm: ip6tables Not tainted 6.12.0-rc4-00047-gc2ee9f594da8-dirty #205
Hardware name: QEMU Standard PC (i440FX + PIIX, 1996),
BIOS rel-1.13.0-0-gf21b5a4aeb02-prebuilt.qemu.org 04/01/2014
RIP: 0010:module_put+0x6f/0x80
Call Trace:
 <TASK>
 get_info+0x128/0x180
 do_ip6t_get_ctl+0x6a/0x430
 nf_getsockopt+0x46/0x80
 ipv6_getsockopt+0xb9/0x100
 rawv6_getsockopt+0x42/0x190
 do_sock_getsockopt+0xaa/0x180
 __sys_getsockopt+0x70/0xc0
 __x64_sys_getsockopt+0x20/0x30
 do_syscall_64+0xa2/0x1a0
 entry_SYSCALL_64_after_hwframe+0x77/0x7f

Concurrent execution of module unload and get_info() trigered the warning.
The root cause is as follows:

cpu0				      cpu1
module_exit
//mod->state = MODULE_STATE_GOING
  ip6table_nat_exit
    xt_unregister_template
	kfree(t)
	//removed from templ_list
				      getinfo()
					  t = xt_find_table_lock
						list_for_each_entry(tmpl, &xt_templates[af]...)
							if (strcmp(tmpl->name, name))
								continue;  //table not found
							try_module_get
						list_for_each_entry(t, &xt_net->tables[af]...)
							return t;  //not get refcnt
					  module_put(t->me) //uaf
    unregister_pernet_subsys
    //remove table from xt_net list

While xt_table module was going away and has been removed from
xt_templates list, we couldnt get refcnt of xt_table->me. Check
module in xt_net->tables list re-traversal to fix it.

## References
- https://git.kernel.org/stable/c/6a1f088f9807f5166f58902d26246d0b88da03a8
- https://git.kernel.org/stable/c/ba22ea01348384df19cc1fabc7964be6e7189749
- https://git.kernel.org/stable/c/bab3bb35c03b263c486833d50d50c081d9e9832b
- https://git.kernel.org/stable/c/cb7c388b5967946f097afdb759b7c860305f2d96
- https://git.kernel.org/stable/c/f48d258f0ac540f00fa617dac496c4c18b5dc2fa
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50257.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50257
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
