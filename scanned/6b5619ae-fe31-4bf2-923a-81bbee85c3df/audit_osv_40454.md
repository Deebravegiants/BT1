# [H] xfrm: iptfs: fix use-after-free on first_skb in __input_process_payload

## Summary
Severity: High
Advisory: CVE-2026-53240
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-53240
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.14.0 <6.18.36, >=6.19.0 <7.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

xfrm: iptfs: fix use-after-free on first_skb in __input_process_payload

__input_process_payload() stores first_skb into xtfs->ra_newskb under
drop_lock when starting partial reassembly, then unlocks and breaks out
of the processing loop. The post-loop check reads xtfs->ra_newskb
without the lock to decide whether first_skb is still owned:

    if (first_skb && first_iplen && !defer && first_skb != xtfs->ra_newskb)

Between spin_unlock and this read, a concurrent CPU running
iptfs_reassem_cont() (or the drop_timer hrtimer) can complete
reassembly, NULL xtfs->ra_newskb, and free the skb. The check then
evaluates first_skb != NULL as true, and pskb_trim/ip_summed/consume_skb
operate on the freed skb — a use-after-free in skbuff_head_cache.

Replace the unlocked read with a local bool that records whether
first_skb was handed to the reassembly state in the current call. The
flag is set after the existing spin_unlock, before the break, using the
pointer equality that is stable at that point (first_skb == skb iff
first_skb was stored in ra_newskb).

## References
- https://git.kernel.org/stable/c/8d9a79fbf5172d9c4c0146057af2360913265a11
- https://git.kernel.org/stable/c/eb48730bb827d1550401a5d391903f9d90b493c8
- https://git.kernel.org/stable/c/ff2ee35b6ce5fa8a8e24ea50b15733d5c8780198
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53240.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53240
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
