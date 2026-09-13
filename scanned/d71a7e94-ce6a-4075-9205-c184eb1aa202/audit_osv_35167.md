# [H] bnxt_en: Fix XDP_TX path

## Summary
Severity: High
Advisory: CVE-2025-68770
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-01-13
Source: https://osv.dev/vulnerability/CVE-2025-68770
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.12.64, >=6.13.0 <6.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

bnxt_en: Fix XDP_TX path

For XDP_TX action in bnxt_rx_xdp(), clearing of the event flags is not
correct.  __bnxt_poll_work() -> bnxt_rx_pkt() -> bnxt_rx_xdp() may be
looping within NAPI and some event flags may be set in earlier
iterations.  In particular, if BNXT_TX_EVENT is set earlier indicating
some XDP_TX packets are ready and pending, it will be cleared if it is
XDP_TX action again.  Normally, we will set BNXT_TX_EVENT again when we
successfully call __bnxt_xmit_xdp().  But if the TX ring has no more
room, the flag will not be set.  This will cause the TX producer to be
ahead but the driver will not hit the TX doorbell.

For multi-buf XDP_TX, there is no need to clear the event flags and set
BNXT_AGG_EVENT.  The BNXT_AGG_EVENT flag should have been set earlier in
bnxt_rx_pkt().

The visible symptom of this is that the RX ring associated with the
TX XDP ring will eventually become empty and all packets will be dropped.
Because this condition will cause the driver to not refill the RX ring
seeing that the TX ring has forever pending XDP_TX packets.

The fix is to only clear BNXT_RX_EVENT when we have successfully
called __bnxt_xmit_xdp().

## References
- https://git.kernel.org/stable/c/0373d5c387f24de749cc22e694a14b3a7c7eb515
- https://git.kernel.org/stable/c/4b83902a1e67ff327ab5c6c65021a03e72c081d6
- https://git.kernel.org/stable/c/f17e0c1208485b24d61271bc1ddc8f2087e71561
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68770.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-68770
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
