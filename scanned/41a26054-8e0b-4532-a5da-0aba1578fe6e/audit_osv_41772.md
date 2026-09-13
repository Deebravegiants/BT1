# [H] mac802154: llsec: add skb_cow_data() before in-place crypto

## Summary
Severity: High
Advisory: CVE-2026-63831
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63831
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.16.0 <5.10.260, >=5.11.0 <5.15.211, >=5.16.0 <6.1.177, >=6.2.0 <6.6.144, >=6.7.0 <6.12.95, >=6.13.0 <6.18.38, >=6.19.0 <7.1.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

mac802154: llsec: add skb_cow_data() before in-place crypto

llsec_do_encrypt_unauth(), llsec_do_encrypt_auth(),
llsec_do_decrypt_unauth(), and llsec_do_decrypt_auth() all perform
in-place cryptographic transformations on skb data.  They build a
scatterlist with sg_init_one() pointing into the skb's linear data area
and then pass the same scatterlist as both src and dst to the crypto API
(e.g. crypto_skcipher_encrypt/decrypt, crypto_aead_encrypt/decrypt).

On the RX path, __ieee802154_rx_handle_packet() clones the received skb
before handing it to each subscriber via ieee802154_subif_frame().  The
cloned skb shares the same underlying data buffer via reference
counting.  When llsec_do_decrypt() subsequently modifies this shared
buffer in place, it corrupts data that other clones -- potentially
belonging to other sockets or subsystems -- still reference.

On the TX path, similar data sharing can occur when an skb's head has
been cloned (skb_cloned() returns true).

The fix is to call skb_cow_data() before performing any in-place crypto
operation.  skb_cow_data() ensures that the skb's data area is not
shared: if the skb head is cloned or the data spans multiple fragments,
it copies the data into a private buffer that can be safely modified in
place.  This is the same pattern used by:

  - ESP (net/ipv4/esp4.c, net/ipv6/esp6.c)
  - MACsec (drivers/net/macsec.c)
  - WireGuard (drivers/net/wireguard/receive.c)
  - TIPC (net/tipc/crypto.c)

Without this guard, in-place crypto on shared skb data leads to:
  - Silent data corruption of other skb clones
  - Use-after-free when the crypto API scatterwalk writes through a
    page that has already been freed by another clone's kfree_skb()
  - Kernel crashes under concurrent 802.15.4 traffic with security
    enabled (KASAN/KMSAN reports slab-use-after-free)

Found by 0sec (https://0sec.ai) using automated source analysis.

## References
- https://git.kernel.org/stable/c/3a2b378b3a9ca75d3518d879148d2ad25b5714a9
- https://git.kernel.org/stable/c/7a831bcd0486788283ef35e396d4282ee01bb0d5
- https://git.kernel.org/stable/c/84a04eb5b210643bd67aab81ff805d32f62aa865
- https://git.kernel.org/stable/c/86d531337ea1ba02d9f2bc830d07c683d9bfaade
- https://git.kernel.org/stable/c/993fd674fe85d114e6a8d3963033d4fbbc2170a8
- https://git.kernel.org/stable/c/bd968bdd568beacfdf98ec537a87527e85f1d0cf
- https://git.kernel.org/stable/c/e28e7fd34c449028325322a3f5127b92594b7396
- https://git.kernel.org/stable/c/ff976ef7c39199ebff33c18034636595016db9f0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63831.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63831
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
