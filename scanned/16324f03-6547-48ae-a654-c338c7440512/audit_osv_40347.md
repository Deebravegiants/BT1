# [H] pppoe: drop PFC frames

## Summary
Severity: High
Advisory: CVE-2026-53003
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-53003
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.0.0 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.141, >=6.7.0 <6.12.91, >=6.13.0 <6.18.33, >=6.19.0 <7.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

pppoe: drop PFC frames

RFC 2516 Section 7 states that Protocol Field Compression (PFC) is NOT
RECOMMENDED for PPPoE. In practice, pppd does not support negotiating
PFC for PPPoE sessions, and the current PPPoE driver assumes an
uncompressed (2-byte) protocol field. However, the generic PPP layer
function ppp_input() is not aware of the negotiation result, and still
accepts PFC frames.

If a peer with a broken implementation or an attacker sends a frame with
a compressed (1-byte) protocol field, the subsequent PPP payload is
shifted by one byte. This causes the network header to be 4-byte
misaligned, which may trigger unaligned access exceptions on some
architectures.

To reduce the attack surface, drop PPPoE PFC frames. Introduce
ppp_skb_is_compressed_proto() helper function to be used in both
ppp_generic.c and pppoe.c to avoid open-coding.

## References
- https://git.kernel.org/stable/c/0cab5d077dd1efd2bd1a47271acc35894f945b4f
- https://git.kernel.org/stable/c/2b5c3c040d020e3ab3b9a8887031202d96843b1e
- https://git.kernel.org/stable/c/49e41b60ccd1bdbe9e218420f716dd5f9a2f9c71
- https://git.kernel.org/stable/c/8a5e840babc5c0fbd10c73728a13192347771ec6
- https://git.kernel.org/stable/c/ba758fdf1399f310b30098b6faa3fd043de47dd2
- https://git.kernel.org/stable/c/cb3beef35ab5e0c1afca9fd7648c6ae499786377
- https://git.kernel.org/stable/c/cc1ff87bce1ccd38410ab10960f576dcd17db679
- https://git.kernel.org/stable/c/fcca1df05322bb04e344dd1178b54b76a08eb7c3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53003.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53003
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
