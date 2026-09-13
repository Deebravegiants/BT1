# [H] CVE-2021-47520

## Summary
Severity: High
Advisory: CVE-2021-47520
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-24
Source: https://osv.dev/vulnerability/CVE-2021-47520
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

can: pch_can: pch_can_rx_normal: fix use after free

After calling netif_receive_skb(skb), dereferencing skb is unsafe.
Especially, the can_frame cf which aliases skb memory is dereferenced
just after the call netif_receive_skb(skb).

Reordering the lines solves the issue.

## References
- https://git.kernel.org/stable/c/6c73fc931658d8cbc8a1714b326cb31eb71d16a7
- https://git.kernel.org/stable/c/703dde112021c93d6e89443c070e7dbd4dea612e
- https://git.kernel.org/stable/c/94cddf1e9227a171b27292509d59691819c458db
- https://git.kernel.org/stable/c/abb4eff3dcd2e583060082a18a8dbf31f02689d4
- https://git.kernel.org/stable/c/affbad02bf80380a7403885b9fe4a1587d1bb4f3
- https://git.kernel.org/stable/c/bafe343a885c70dddf358379cf0b2a1c07355d8d
- https://git.kernel.org/stable/c/3a3c46e2eff0577454860a203be1a8295f4acb76
- https://git.kernel.org/stable/c/3e193ef4e0a3f5bf92ede83ef214cb09d01b00aa
