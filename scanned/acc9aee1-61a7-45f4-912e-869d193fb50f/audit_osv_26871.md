# [H] netfilter: ebtables: fix table blob use-after-free

## Summary
Severity: High
Advisory: CVE-2023-54243
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-30
Source: https://osv.dev/vulnerability/CVE-2023-54243
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.15.0 <5.10.173, >=5.11.0 <5.15.100, >=5.16.0 <6.1.18, >=6.2.0 <6.2.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: ebtables: fix table blob use-after-free

We are not allowed to return an error at this point.
Looking at the code it looks like ret is always 0 at this
point, but its not.

t = find_table_lock(net, repl->name, &ret, &ebt_mutex);

... this can return a valid table, with ret != 0.

This bug causes update of table->private with the new
blob, but then frees the blob right away in the caller.

Syzbot report:

BUG: KASAN: vmalloc-out-of-bounds in __ebt_unregister_table+0xc00/0xcd0 net/bridge/netfilter/ebtables.c:1168
Read of size 4 at addr ffffc90005425000 by task kworker/u4:4/74
Workqueue: netns cleanup_net
Call Trace:
 kasan_report+0xbf/0x1f0 mm/kasan/report.c:517
 __ebt_unregister_table+0xc00/0xcd0 net/bridge/netfilter/ebtables.c:1168
 ebt_unregister_table+0x35/0x40 net/bridge/netfilter/ebtables.c:1372
 ops_exit_list+0xb0/0x170 net/core/net_namespace.c:169
 cleanup_net+0x4ee/0xb10 net/core/net_namespace.c:613
...

ip(6)tables appears to be ok (ret should be 0 at this point) but make
this more obvious.

## References
- https://git.kernel.org/stable/c/3dd6ac973351308d4117eda32298a9f1d68764fd
- https://git.kernel.org/stable/c/9060abce3305ab2354c892c09d5689df51486df5
- https://git.kernel.org/stable/c/cda0e0243bd3c04008fcd37a46b0269fb3c49249
- https://git.kernel.org/stable/c/dbb3cbbf03b3c52cb390fabec357f1e4638004f5
- https://git.kernel.org/stable/c/e58a171d35e32e6e8c37cfe0e8a94406732a331f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/54xxx/CVE-2023-54243.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-54243
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
