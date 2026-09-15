# [H] net/sched: act_ct: preserve tc_skb_cb across defragmentation

## Summary
Severity: High
Advisory: CVE-2026-72057
Ecosystem: Linux
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72057
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.15.217, >=5.16.0 <6.6.145, >=6.2.0 <6.12.97, >=6.7.0 <6.18.40, >=6.13.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/sched: act_ct: preserve tc_skb_cb across defragmentation

tcf_ct_handle_fragments() calls nf_ct_handle_fragments() without saving
and restoring skb->cb. The defrag helper clears IPCB/IP6CB, which aliases
the tc_skb_cb/qdisc_skb_cb control buffer. Fragmented traffic through
act_ct therefore loses qdisc metadata such as pkt_segs and can trigger
WARN_ON_ONCE() in qdisc_pkt_segs() when panic_on_warn is enabled.

Save and restore the full tc_skb_cb around nf_ct_handle_fragments(),
matching the pattern used by ovs_ct_handle_fragments().

## References
- https://git.kernel.org/stable/c/2400c4b05d58834b994500a9eec90a37db44187c
- https://git.kernel.org/stable/c/5c3ae5f6c7c6de73ea9b6a75154fe4ed343e1bac
- https://git.kernel.org/stable/c/67d6b00a54446c008f52cf70fc0c2ad0c712f85d
- https://git.kernel.org/stable/c/9092e15defbe6c7bc241c306093ca9d358a578e7
- https://git.kernel.org/stable/c/b3d835407846134b0d54637c0281b39bebef831d
- https://git.kernel.org/stable/c/f7f45ceb855d9ba1cba594fb3f383255f7013fad
- https://git.kernel.org/stable/c/fb080b6f54835d5d4d11ce3122800e6f0f6689e6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72057.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72057
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
