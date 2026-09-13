# [H] vsock/virtio: bind uarg before filling zerocopy skb

## Summary
Severity: High
Advisory: CVE-2026-63970
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63970
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.7.0 <6.12.97, >=6.13.0 <6.18.35, >=6.19.0 <7.0.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

vsock/virtio: bind uarg before filling zerocopy skb

virtio_transport_send_pkt_info() allocates or reuses the zerocopy uarg
before entering the send loop, but virtio_transport_alloc_skb() still
fills the skb before it inherits that uarg. When fixed-buffer vectored
zerocopy hits MAX_SKB_FRAGS, io_sg_from_iter() may partially attach
managed frags and return -EMSGSIZE. The rollback path call kfree_skb()
to free an skb that carries SKBFL_MANAGED_FRAG_REFS but no uarg, so
skb_release_data() falls through to ordinary frag unref.

Pass the uarg into virtio_transport_alloc_skb() and bind it immediately
before virtio_transport_fill_skb(). This keeps control or no-payload skbs
untouched while ensuring success and rollback share one lifetime rule.

## References
- https://git.kernel.org/stable/c/1e584c304cfb94a759417130b1fc6d30b30c4cce
- https://git.kernel.org/stable/c/5d317573f1d48e76cce5fb6250452b6e4102e0fb
- https://git.kernel.org/stable/c/72194f65050958e4c8e069adb6c5d89ef81ca197
- https://git.kernel.org/stable/c/b62e2b2b4a50953ca952f3cd3f77dd62dc50fd5d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63970.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63970
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
