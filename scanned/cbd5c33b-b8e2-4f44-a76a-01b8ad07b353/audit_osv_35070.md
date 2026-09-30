# [C] net: usb: qmi_wwan: initialize MAC header offset in qmimux_rx_fixup

## Summary
Severity: Critical
Advisory: CVE-2025-68192
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-16
Source: https://osv.dev/vulnerability/CVE-2025-68192
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.12.0 <5.4.302, >=5.5.0 <5.10.247, >=5.11.0 <5.15.197, >=5.16.0 <6.1.159, >=6.2.0 <6.6.117, >=6.7.0 <6.12.58, >=6.13.0 <6.17.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: usb: qmi_wwan: initialize MAC header offset in qmimux_rx_fixup

Raw IP packets have no MAC header, leaving skb->mac_header uninitialized.
This can trigger kernel panics on ARM64 when xfrm or other subsystems
access the offset due to strict alignment checks.

Initialize the MAC header to prevent such crashes.

This can trigger kernel panics on ARM when running IPsec over the
qmimux0 interface.

Example trace:

    Internal error: Oops: 000000009600004f [#1] SMP
    CPU: 0 UID: 0 PID: 0 Comm: swapper/0 Not tainted 6.12.34-gbe78e49cb433 #1
    Hardware name: LS1028A RDB Board (DT)
    pstate: 60000005 (nZCv daif -PAN -UAO -TCO -DIT -SSBS BTYPE=--)
    pc : xfrm_input+0xde8/0x1318
    lr : xfrm_input+0x61c/0x1318
    sp : ffff800080003b20
    Call trace:
     xfrm_input+0xde8/0x1318
     xfrm6_rcv+0x38/0x44
     xfrm6_esp_rcv+0x48/0xa8
     ip6_protocol_deliver_rcu+0x94/0x4b0
     ip6_input_finish+0x44/0x70
     ip6_input+0x44/0xc0
     ipv6_rcv+0x6c/0x114
     __netif_receive_skb_one_core+0x5c/0x8c
     __netif_receive_skb+0x18/0x60
     process_backlog+0x78/0x17c
     __napi_poll+0x38/0x180
     net_rx_action+0x168/0x2f0

## References
- https://git.kernel.org/stable/c/0aabccdcec1f4a36f95829ea2263f845bbc77223
- https://git.kernel.org/stable/c/4e6b9004f01d0fef5b19778399bc5bf55f8c2d71
- https://git.kernel.org/stable/c/8ab3b8f958d861a7f725a5be60769106509fbd69
- https://git.kernel.org/stable/c/ae811175cea35b03ac6d7c910f43a82a43b9c3b3
- https://git.kernel.org/stable/c/bf527b80b80a282ab5bf1540546211fc35e5cd42
- https://git.kernel.org/stable/c/d693c47fb902b988f5752182e4f7fbde5e6dcaf9
- https://git.kernel.org/stable/c/dd03780c29f87c26c0e0bb7e0db528c8109461fb
- https://git.kernel.org/stable/c/e120f46768d98151ece8756ebd688b0e43dc8b29
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68192.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-68192
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
