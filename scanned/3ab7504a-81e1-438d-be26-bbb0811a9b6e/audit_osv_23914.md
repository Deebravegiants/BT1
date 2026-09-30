# [H] net: bonding: fix use-after-free after 802.3ad slave unbind

## Summary
Severity: High
Advisory: CVE-2022-49667
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49667
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.7.0 <4.9.322, >=4.10.0 <4.14.287, >=4.15.0 <4.19.251, >=4.20.0 <5.4.204, >=5.5.0 <5.10.129, >=5.11.0 <5.15.53, >=5.16.0 <5.18.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: bonding: fix use-after-free after 802.3ad slave unbind

commit 0622cab0341c ("bonding: fix 802.3ad aggregator reselection"),
resolve case, when there is several aggregation groups in the same bond.
bond_3ad_unbind_slave will invalidate (clear) aggregator when
__agg_active_ports return zero. So, ad_clear_agg can be executed even, when
num_of_ports!=0. Than bond_3ad_unbind_slave can be executed again for,
previously cleared aggregator. NOTE: at this time bond_3ad_unbind_slave
will not update slave ports list, because lag_ports==NULL. So, here we
got slave ports, pointing to freed aggregator memory.

Fix with checking actual number of ports in group (as was before
commit 0622cab0341c ("bonding: fix 802.3ad aggregator reselection") ),
before ad_clear_agg().

The KASAN logs are as follows:

[  767.617392] ==================================================================
[  767.630776] BUG: KASAN: use-after-free in bond_3ad_state_machine_handler+0x13dc/0x1470
[  767.638764] Read of size 2 at addr ffff00011ba9d430 by task kworker/u8:7/767
[  767.647361] CPU: 3 PID: 767 Comm: kworker/u8:7 Tainted: G           O 5.15.11 #15
[  767.655329] Hardware name: DNI AmazonGo1 A7040 board (DT)
[  767.660760] Workqueue: lacp_1 bond_3ad_state_machine_handler
[  767.666468] Call trace:
[  767.668930]  dump_backtrace+0x0/0x2d0
[  767.672625]  show_stack+0x24/0x30
[  767.675965]  dump_stack_lvl+0x68/0x84
[  767.679659]  print_address_description.constprop.0+0x74/0x2b8
[  767.685451]  kasan_report+0x1f0/0x260
[  767.689148]  __asan_load2+0x94/0xd0
[  767.692667]  bond_3ad_state_machine_handler+0x13dc/0x1470

## References
- https://git.kernel.org/stable/c/050133e1aa2cb49bb17be847d48a4431598ef562
- https://git.kernel.org/stable/c/2765749def4765c5052a4c66445cf4c96fcccdbc
- https://git.kernel.org/stable/c/63b2fe509f69b90168a75e04e14573dccf7984e6
- https://git.kernel.org/stable/c/893825289ba840afd86bfffcb6f7f363c73efff8
- https://git.kernel.org/stable/c/a853b7a3a9fd1d74a4ccdd9cd73512b7dace2f1e
- https://git.kernel.org/stable/c/b90ac60303063a43e17dd4aec159067599d255e6
- https://git.kernel.org/stable/c/ef0af7d08d26c5333ff4944a559279464edf6f15
- https://git.kernel.org/stable/c/f162f7c348fa2a5555bafdb5cc890b89b221e69c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49667.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49667
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
