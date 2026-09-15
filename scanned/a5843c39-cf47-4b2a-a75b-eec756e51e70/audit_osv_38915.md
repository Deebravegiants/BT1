# [H] net: correctly handle tunneled traffic on IPV6_CSUM GSO fallback

## Summary
Severity: High
Advisory: CVE-2026-43057
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-01
Source: https://osv.dev/vulnerability/CVE-2026-43057
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.1.168, >=6.2.0 <6.6.134, >=6.7.0 <6.12.81, >=6.13.0 <6.18.22, >=6.17.0 <6.19.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: correctly handle tunneled traffic on IPV6_CSUM GSO fallback

NETIF_F_IPV6_CSUM only advertises support for checksum offload of
packets without IPv6 extension headers. Packets with extension
headers must fall back onto software checksumming. Since TSO
depends on checksum offload, those must revert to GSO.

The below commit introduces that fallback. It always checks
network header length. For tunneled packets, the inner header length
must be checked instead. Extend the check accordingly.

A special case is tunneled packets without inner IP protocol. Such as
RFC 6951 SCTP in UDP. Those are not standard IPv6 followed by
transport header either, so also must revert to the software GSO path.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://git.kernel.org/stable/c/2094a7cf91b71367b649f991aacc7b579f793d0b
- https://git.kernel.org/stable/c/33670f780e0120c3dacda188c512bbffe0b6044c
- https://git.kernel.org/stable/c/732fdeb2987c94b439d51f5cb9addddc2fc48c42
- https://git.kernel.org/stable/c/a98b78116a27e2a57b696b569b2cb431c95cf9b6
- https://git.kernel.org/stable/c/c4336a07eb6b2526dc2b62928b5104b41a7f81f5
- https://git.kernel.org/stable/c/ed71cf465c75f5688b07a35d373cd1d6b589c8ea
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43057.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43057
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
