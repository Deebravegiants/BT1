# [H] Bluetooth: HIDP: reject frames without a transaction header

## Summary
Severity: High
Advisory: CVE-2026-74508
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74508
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.10.266, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.151, >=6.7.0 <6.12.103, >=6.13.0 <6.18.44, >=6.19.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: HIDP: reject frames without a transaction header

hidp_recv_ctrl_frame() and hidp_recv_intr_frame() read skb->data[0]
before checking that the L2CAP SDU contains a transaction header. A
connected HIDP peer can send an empty basic-mode SDU and make both paths
use an uninitialized byte from skb tailroom.

KMSAN reports the use in hidp_session_run(), with the uninitialized value
originating in __alloc_skb() through vhci_write(). The control path
produces two reports and the interrupt path produces one.

The byte can also be controlled by a malformed lower-layer packet. If an
HCI ACL packet contains an L2CAP PDU with a declared zero-length payload
followed by an extra 0x15 byte, l2cap_recv_acldata() reduces skb->len to
the declared PDU length before dispatch. The current HIDP path nevertheless
consumes the extra byte as HIDP_TRANS_HID_CONTROL |
HIDP_CTRL_VIRTUAL_CABLE_UNPLUG and terminates the HIDP session. With this
change, the same packet is discarded and a subsequent feature report
request succeeds.

Pull the transaction header with skb_pull_data() and discard frames that
do not contain it.

## References
- https://git.kernel.org/stable/c/238c333bc4b3f245c626632e8bfa3c9dab97f51b
- https://git.kernel.org/stable/c/24c64ccd5c1fc9934b427335b0d976c7f2b1a7d8
- https://git.kernel.org/stable/c/2ebf63aa557a69990b4e9ea22be224d58aabce96
- https://git.kernel.org/stable/c/46ca5ab39737d7c6f9ca77ecf714cdcfa6caaeec
- https://git.kernel.org/stable/c/47778d2c2087b5d192398f6fddf692d16a5431cf
- https://git.kernel.org/stable/c/567a2a0a633f2ea5fdccaf3517c09f22c9d860c7
- https://git.kernel.org/stable/c/854194494a6f726a60b90b76059148bf08df023d
- https://git.kernel.org/stable/c/97b61241ab45bfa5b0526cb0f3978942493bc811
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74508.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74508
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
