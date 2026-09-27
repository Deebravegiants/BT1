# [H] skbuff: Fix a race between coalescing and releasing SKBs

## Summary
Severity: High
Advisory: CVE-2023-53186
Ecosystem: Linux
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-15
Source: https://osv.dev/vulnerability/CVE-2023-53186
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.108, >=5.16.0 <6.1.25, >=6.2.0 <6.2.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

skbuff: Fix a race between coalescing and releasing SKBs

Commit 1effe8ca4e34 ("skbuff: fix coalescing for page_pool fragment
recycling") allowed coalescing to proceed with non page pool page and page
pool page when @from is cloned, i.e.

to->pp_recycle    --> false
from->pp_recycle  --> true
skb_cloned(from)  --> true

However, it actually requires skb_cloned(@from) to hold true until
coalescing finishes in this situation. If the other cloned SKB is
released while the merging is in process, from_shinfo->nr_frags will be
set to 0 toward the end of the function, causing the increment of frag
page _refcount to be unexpectedly skipped resulting in inconsistent
reference counts. Later when SKB(@to) is released, it frees the page
directly even though the page pool page is still in use, leading to
use-after-free or double-free errors. So it should be prohibited.

The double-free error message below prompted us to investigate:
BUG: Bad page state in process swapper/1  pfn:0e0d1
page:00000000c6548b28 refcount:-1 mapcount:0 mapping:0000000000000000
index:0x2 pfn:0xe0d1
flags: 0xfffffc0000000(node=0|zone=1|lastcpupid=0x1fffff)
raw: 000fffffc0000000 0000000000000000 ffffffff00000101 0000000000000000
raw: 0000000000000002 0000000000000000 ffffffffffffffff 0000000000000000
page dumped because: nonzero _refcount

CPU: 1 PID: 0 Comm: swapper/1 Tainted: G            E      6.2.0+
Call Trace:
 <IRQ>
dump_stack_lvl+0x32/0x50
bad_page+0x69/0xf0
free_pcp_prepare+0x260/0x2f0
free_unref_page+0x20/0x1c0
skb_release_data+0x10b/0x1a0
napi_consume_skb+0x56/0x150
net_rx_action+0xf0/0x350
? __napi_schedule+0x79/0x90
__do_softirq+0xc8/0x2b1
__irq_exit_rcu+0xb9/0xf0
common_interrupt+0x82/0xa0
</IRQ>
<TASK>
asm_common_interrupt+0x22/0x40
RIP: 0010:default_idle+0xb/0x20

## References
- https://git.kernel.org/stable/c/0646dc31ca886693274df5749cd0c8c1eaaeb5ca
- https://git.kernel.org/stable/c/5f692c992a3bb9a8018e3488098b401a4229e7ec
- https://git.kernel.org/stable/c/71850b5af92da21b4862a9bc55bda61091247d00
- https://git.kernel.org/stable/c/906a6689bb0191ad2a44131a3377006aa098af59
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53186.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53186
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
