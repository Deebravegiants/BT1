# [C] ixgbevf: fix use-after-free in VEPA multicast source pruning

## Summary
Severity: Critical
Advisory: CVE-2026-64113
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64113
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.19.0 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.142, >=6.7.0 <6.12.92, >=6.13.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

ixgbevf: fix use-after-free in VEPA multicast source pruning

ixgbevf_clean_rx_irq() prunes frames whose source MAC matches the VF's
own address (VEPA multicast workaround) by freeing the skb and
continuing to the next descriptor:

    dev_kfree_skb_irq(skb);
    continue;

The skb pointer is declared outside the while loop and persists across
iterations.  Because the continue skips the "skb = NULL" reset at the
bottom of the loop, the next iteration enters the "else if (skb)" path
and calls ixgbevf_add_rx_frag() on the freed skb, dereferencing
skb_shinfo(skb)->nr_frags - a use-after-free in NAPI softirq context.

The sibling driver iavf already handles this correctly by nulling the
pointer before continuing.  Apply the same pattern here.

I do not have ixgbevf hardware; the bug was found by static analysis
(scan_drop_continue_loops.py + semgrep drop_continue_in_loop, multi-tool
corroboration with the highest score in the scan).  The UAF was confirmed
under KASAN by loading a test module that reproduces the exact code
pattern (alloc skb, kfree_skb, then read skb_shinfo(skb)->nr_frags):

  BUG: KASAN: slab-use-after-free in ixgbevf_uaf_test_init+0x100/0x1000
  Read of size 8 at addr 000000006163ae78 by task insmod/30
  freed 208-byte region [000000006163adc0, 000000006163ae90)

QEMU emulates igb (82576) but not ixgbe (82599), and the igbvf VF
driver does not include the VEPA source pruning path, so a full
end-to-end reproduction with emulated hardware was not possible.

## References
- https://git.kernel.org/stable/c/3d931ac62411a7e43b85dba5fe45e1a4a91bd5cb
- https://git.kernel.org/stable/c/55b3e91d62b2f7a24109b2d7c9f4c66d2e3b1ec1
- https://git.kernel.org/stable/c/5d49b568c188dc77199d8d2b959c91da8cc27cf1
- https://git.kernel.org/stable/c/6ef30384a50a50e4a484cddf341bc27de31aa3de
- https://git.kernel.org/stable/c/a244395d8c563ed1bb26c3ef708db6aeeaa08084
- https://git.kernel.org/stable/c/add70e2682c0ad3be2a5810bcf1bc13963ba4df9
- https://git.kernel.org/stable/c/dfef79e09ed2f5df975c98547f97f5d7f8982a24
- https://git.kernel.org/stable/c/e8768bcbe5cd30c4ea36a22022c9ffaa66903693
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64113.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64113
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
