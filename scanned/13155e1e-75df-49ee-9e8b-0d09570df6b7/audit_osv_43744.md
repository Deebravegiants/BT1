# [H] packet: synchronize pressure clearing with ring reconfiguration

## Summary
Severity: High
Advisory: CVE-2026-74666
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-74666
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.2.0 <5.10.267, >=5.11.0 <5.15.218, >=5.16.0 <6.1.185, >=6.2.0 <6.6.152, >=6.7.0 <6.12.104, >=6.13.0 <6.18.45, >=6.19.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

packet: synchronize pressure clearing with ring reconfiguration

packet_set_ring() updates the RX ring state under sk_receive_queue.lock,
but used to publish the tpacket receive mode through po->prot_hook.func
after releasing that lock. packet_poll() and packet_recvmsg() can then
run the pressure clearing path after the ring has been cleared while
still seeing tpacket_rcv, causing __packet_rcv_has_room() to dereference
stale or NULL ring storage.

Move the existing receive hook assignment into the same
sk_receive_queue.lock section as the ring state update. Keep the
assignment otherwise unchanged, including on TX ring reconfiguration, to
avoid adding behavior changes that are not required for the fix.

Serialize packet_recvmsg() pressure clearing with the same queue lock
only after PACKET_SOCK_PRESSURE has been observed. If the flag is clear
and the socket has moved away from tpacket_rcv, packet_set_ring() has
already detached the socket and waited for synchronize_net(), so no new
packet input can set the flag again.

packet_poll() already holds sk_receive_queue.lock, so it uses the new
unlocked helper directly.

## References
- https://git.kernel.org/stable/c/1a35da325cac4d5bcad76a2aa943408a6f1d9000
- https://git.kernel.org/stable/c/2c7b5eb87b2b288cdbde825f21d2b83b2f5da747
- https://git.kernel.org/stable/c/8cfb2e71926a682f36c4240067d424074dd8f70f
- https://git.kernel.org/stable/c/a08196c3cc105947746ec21309edfbb60275fcdb
- https://git.kernel.org/stable/c/ad740b4990347521f0db260d381f9f74e7b340ba
- https://git.kernel.org/stable/c/bf3c8e86bc8ad111be3f3136125e255344bcb3da
- https://git.kernel.org/stable/c/cf8189b82bb93f219ab740e0346c919ad65ada62
- https://git.kernel.org/stable/c/f015c9de92b731814059a343b765c60c0196225c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74666.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74666
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
