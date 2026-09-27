# [H] nfc: hci: fix out-of-bounds read in HCP header parsing

## Summary
Severity: High
Advisory: CVE-2026-63915
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63915
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.5.0 <5.10.259, >=5.11.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.93, >=6.13.0 <6.18.35, >=6.19.0 <7.0.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

nfc: hci: fix out-of-bounds read in HCP header parsing

Both nfc_hci_recv_from_llc() and nci_hci_data_received_cb() read
packet->header from skb->data at function entry without first checking
that the buffer holds at least one byte. A malicious NFC peer can send
a 0-byte HCP frame that passes through the SHDLC layer and reaches
these functions, causing an out-of-bounds heap read of packet->header.
The same 0-byte frame, if queued as a non-final fragment, also causes
the reassembly loop to underflow msg_len to UINT_MAX, triggering
skb_over_panic() when the reassembled skb is written.

Fix this by adding a pskb_may_pull() check at the entry of each
function before packet->header is first accessed. The existing
pskb_may_pull() checks before the reassembled hcp_skb is cast to
struct hcp_packet remain in place to guard the 2-byte HCP message
header.

## References
- https://git.kernel.org/stable/c/1905f5ec3641b2b234bb63549c8ca11ab85466eb
- https://git.kernel.org/stable/c/22d41b176b9989efd21c3b2d3abf6728f05b9d9a
- https://git.kernel.org/stable/c/37382293f174b82a0616c8295e32b1fc8e13d1ed
- https://git.kernel.org/stable/c/83b1362edc9d6ae376c6f36da116e2c70f2e70a6
- https://git.kernel.org/stable/c/b99366d74b535d0cadb1ef73e04639415d9ff3b7
- https://git.kernel.org/stable/c/c4cc6b3b0013acb3ed0b2b60e57dfae98647fe98
- https://git.kernel.org/stable/c/ed6d5d97dad0334a7f43d218753429cbe2f70a4f
- https://git.kernel.org/stable/c/f040e590c035bfd9553fe79ee9585caf1b14d67b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63915.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63915
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
