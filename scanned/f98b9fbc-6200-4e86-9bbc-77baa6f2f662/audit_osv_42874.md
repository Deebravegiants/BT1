# [H] net/mlx5e: macsec: fix use-after-free of metadata_dst on RX SC delete

## Summary
Severity: High
Advisory: CVE-2026-72072
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72072
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.1.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/mlx5e: macsec: fix use-after-free of metadata_dst on RX SC delete

When an offloaded MACsec RX SC is deleted, macsec_del_rxsc_ctx() freed
the per-SC metadata_dst with metadata_dst_free(), which kfree()s the
object unconditionally and ignores the dst reference count. The RX
datapath in mlx5e_macsec_offload_handle_rx_skb() looks up the SC under
rcu_read_lock() via xa_load(), takes a reference with dst_hold() and
attaches the dst to the skb with skb_dst_set(). A reader that already
obtained the rx_sc pointer can race with the delete path and operate on
freed memory.

Fix the owner side by dropping the reference with dst_release() instead
of freeing unconditionally, and convert the RX datapath to
dst_hold_safe() so a reader racing the SC delete cannot attach a dst
whose last reference was just dropped; only attach it when a reference
was actually taken.

mlx5e_macsec_add_rxsc() also published sc_xarray_element via xa_alloc()
before rx_sc->md_dst was allocated and initialised, so a datapath reader
that looked the SC up by fs_id could observe rx_sc with md_dst still
NULL or, on weakly-ordered architectures, a non-NULL md_dst pointer
whose contents were not yet visible. NULL-check the xa_load() result and
md_dst on the datapath, and reorder add_rxsc() so the xa_alloc() publish
happens only after md_dst is fully initialised; the xarray RCU publish
then pairs with the rcu_read_lock()/xa_load() in the datapath.

Note: macsec_del_rxsc_ctx() also kfree()s rx_sc->sc_xarray_element
without an RCU grace period while the same datapath reads it under
rcu_read_lock(); that is a separate pre-existing issue left to a
follow-up patch.

Found by 0sec automated security-research tooling (https://0sec.ai).

## References
- https://git.kernel.org/stable/c/088873af13590ebde10de2ade847f57a05ec61c6
- https://git.kernel.org/stable/c/218cc15a4c907659ad4b0e68c535c61594311205
- https://git.kernel.org/stable/c/4a5073b7b30243658f58b2d2d35a823da7fd34d9
- https://git.kernel.org/stable/c/b1a4d0c568bbb52c7c04f4fce3c097dae89ed6cb
- https://git.kernel.org/stable/c/de74d8fd10291763d97b218f09adcc7513c975e4
- https://git.kernel.org/stable/c/ed3cc4218070d6b98bf5fb456dccae424fd38c4f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72072.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72072
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
