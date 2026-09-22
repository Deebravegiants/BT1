# [H] vsock: Ignore signal/timeout on connect() if already established

## Summary
Severity: High
Advisory: CVE-2025-40248
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-04
Source: https://osv.dev/vulnerability/CVE-2025-40248
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.9.0 <5.4.302, >=5.5.0 <5.10.247, >=5.11.0 <5.15.197, >=5.16.0 <6.1.159, >=6.2.0 <6.6.118, >=6.7.0 <6.12.60, >=6.13.0 <6.17.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

vsock: Ignore signal/timeout on connect() if already established

During connect(), acting on a signal/timeout by disconnecting an already
established socket leads to several issues:

1. connect() invoking vsock_transport_cancel_pkt() ->
   virtio_transport_purge_skbs() may race with sendmsg() invoking
   virtio_transport_get_credit(). This results in a permanently elevated
   `vvs->bytes_unsent`. Which, in turn, confuses the SOCK_LINGER handling.

2. connect() resetting a connected socket's state may race with socket
   being placed in a sockmap. A disconnected socket remaining in a sockmap
   breaks sockmap's assumptions. And gives rise to WARNs.

3. connect() transitioning SS_CONNECTED -> SS_UNCONNECTED allows for a
   transport change/drop after TCP_ESTABLISHED. Which poses a problem for
   any simultaneous sendmsg() or connect() and may result in a
   use-after-free/null-ptr-deref.

Do not disconnect socket on signal/timeout. Keep the logic for unconnected
sockets: they don't linger, can't be placed in a sockmap, are rejected by
sendmsg().

[1]: https://lore.kernel.org/netdev/e07fd95c-9a38-4eea-9638-133e38c2ec9b@rbox.co/
[2]: https://lore.kernel.org/netdev/20250317-vsock-trans-signal-race-v4-0-fc8837f3f1d4@rbox.co/
[3]: https://lore.kernel.org/netdev/60f1b7db-3099-4f6a-875e-af9f6ef194f6@rbox.co/

## References
- https://cert-portal.siemens.com/productcert/html/ssa-253495.html
- https://git.kernel.org/stable/c/002541ef650b742a198e4be363881439bb9d86b4
- https://git.kernel.org/stable/c/3f71753935d648082a8279a97d30efe6b85be680
- https://git.kernel.org/stable/c/5998da5a8208ae9ad7838ba322bccb2bdcd95e81
- https://git.kernel.org/stable/c/67432915145848658149683101104e32f9fd6559
- https://git.kernel.org/stable/c/ab6b19f690d89ae4709fba73a3c4a7911f495b7a
- https://git.kernel.org/stable/c/da664101fb4a0de5cb70d2bae6a650df954df2af
- https://git.kernel.org/stable/c/eeca93f06df89be5a36305b7b9dae1ed65550dfc
- https://git.kernel.org/stable/c/f1c170cae285e4b8f61be043bb17addc3d0a14b5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40248.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40248
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
