# [H] virtio-net: fix len check in receive_big()

## Summary
Severity: High
Advisory: CVE-2026-64552
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-27
Source: https://osv.dev/vulnerability/CVE-2026-64552
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.18.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

virtio-net: fix len check in receive_big()

receive_big() bounds the device-announced length by
(big_packets_num_skbfrags + 1) * PAGE_SIZE.  That is still too loose:
add_recvbuf_big() sets sg[1] to start at offset
sizeof(struct padded_vnet_hdr) into the first page, so the chain
actually carries hdr_len + (PAGE_SIZE - sizeof(padded_vnet_hdr)) +
big_packets_num_skbfrags * PAGE_SIZE bytes -- 20 bytes less than the
check allows for the common hdr_len == 12 case.

A malicious virtio backend can announce a len in that gap.  page_to_skb()
then walks one frag past the page chain, storing a NULL page->private
into skb_shinfo()->frags[MAX_SKB_FRAGS], which is both an out-of-bounds
write past the static frag array and a NULL frag handed up the rx path.

Bound len by the size add_recvbuf_big() actually advertised.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://git.kernel.org/stable/c/38e94d63e29f4a5c6eae87ee2c02101aaa321502
- https://git.kernel.org/stable/c/9e5ad06ea826322ce8c58b4a68442a96f600c3c4
- https://git.kernel.org/stable/c/c7fc9adf4e006155f7f2aeda052fbcde25cdcc49
- https://git.kernel.org/stable/c/e6b8463b7d791f3886d7584259d6e9f06a69f12e
- https://git.kernel.org/stable/c/f9451d0fd5ba635dcabb49bfe456a6db734a8986
- https://git.kernel.org/stable/c/fbeb65154583879d556ea94cb2f15888e9470f3d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64552.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64552
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
