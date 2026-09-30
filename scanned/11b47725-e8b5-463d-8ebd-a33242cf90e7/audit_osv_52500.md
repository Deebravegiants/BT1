# [M] CVE-2021-47515

## Summary
Severity: Medium
Advisory: CVE-2021-47515
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-24
Source: https://osv.dev/vulnerability/CVE-2021-47515
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

seg6: fix the iif in the IPv6 socket control block

When an IPv4 packet is received, the ip_rcv_core(...) sets the receiving
interface index into the IPv4 socket control block (v5.16-rc4,
net/ipv4/ip_input.c line 510):

    IPCB(skb)->iif = skb->skb_iif;

If that IPv4 packet is meant to be encapsulated in an outer IPv6+SRH
header, the seg6_do_srh_encap(...) performs the required encapsulation.
In this case, the seg6_do_srh_encap function clears the IPv6 socket control
block (v5.16-rc4 net/ipv6/seg6_iptunnel.c line 163):

    memset(IP6CB(skb), 0, sizeof(*IP6CB(skb)));

The memset(...) was introduced in commit ef489749aae5 ("ipv6: sr: clear
IP6CB(skb) on SRH ip4ip6 encapsulation") a long time ago (2019-01-29).

Since the IPv6 socket control block and the IPv4 socket control block share
the same memory area (skb->cb), the receiving interface index info is lost
(IP6CB(skb)->iif is set to zero).

As a side effect, that condition triggers a NULL pointer dereference if
commit 0857d6f8c759 ("ipv6: When forwarding count rx stats on the orig
netdev") is applied.

To fix that issue, we set the IP6CB(skb)->iif with the index of the
receiving interface once again.

## References
- https://git.kernel.org/stable/c/ae68d93354e5bf5191ee673982251864ea24dd5c
- https://git.kernel.org/stable/c/b16d412e5f79734033df04e97d7ea2f50a8e9fe3
- https://git.kernel.org/stable/c/ef8804e47c0a44ae106ead1740408af5ea6c6ee9
- https://git.kernel.org/stable/c/6431e71093f3da586a00c6d931481ffb0dc2db0e
- https://git.kernel.org/stable/c/666521b3852d2b2f52d570f9122b1e4b50d96831
- https://git.kernel.org/stable/c/98adb2bbfa407c9290bda299d4c6f7a1c4ebd5e1
