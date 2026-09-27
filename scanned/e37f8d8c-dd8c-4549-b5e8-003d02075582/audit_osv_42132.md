# [C] xfrm: iptfs: propagate SKBFL_SHARED_FRAG in iptfs_skb_add_frags()

## Summary
Severity: Critical
Advisory: CVE-2026-64566
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-64566
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.14.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

xfrm: iptfs: propagate SKBFL_SHARED_FRAG in iptfs_skb_add_frags()

When iptfs_skb_add_frags() copies frag references from the source
frag walk into a new SKB, it increments the page reference count via
__skb_frag_ref() but does not propagate SKBFL_SHARED_FRAG to the
destination SKB's skb_shinfo->flags.

If the source SKB carries shared frags (e.g. from a page-pool backed
receive path), the new inner SKB will appear to ESP as having privately
owned frags.  A subsequent esp_input() call for a nested transport-mode
SA then takes the no-COW fast path and decrypts in place, writing over
pages that are still referenced by the outer IPTFS SKB.  This causes
kernel-visible memory corruption and can trigger a panic.

All other frag-transfer helpers in the kernel (skb_try_coalesce,
skb_gro_receive, __pskb_copy_fclone, skb_shift, skb_segment) correctly
propagate SKBFL_SHARED_FRAG; align iptfs_skb_add_frags() with this
convention by setting the flag inside the loop immediately after
__skb_frag_ref() and nr_frags++, so every exit path that attaches a frag
unconditionally propagates SKBFL_SHARED_FRAG.

## References
- https://git.kernel.org/stable/c/430ea57d6daf765e88f90046afbfd1e071cb7200
- https://git.kernel.org/stable/c/d8aaf06b29f5a0b6186cf68d21c7d63678ee3891
- https://git.kernel.org/stable/c/ffd64e0717efd83fbf3396ab4e5ac6d795dac4d0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64566.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64566
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
