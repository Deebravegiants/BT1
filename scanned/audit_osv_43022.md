# [C] qede: fix off-by-one in BD ring consumption on build_skb failure

## Summary
Severity: Critical
Advisory: CVE-2026-72339
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72339
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.18.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

qede: fix off-by-one in BD ring consumption on build_skb failure

qede_rx_build_skb() and qede_tpa_rx_build_skb() do not check for a
NULL return from qede_build_skb(). When it returns NULL under memory
pressure, the functions still consume a BD from the ring before
returning NULL. The callers then recycle additional BDs, resulting in
one extra BD being consumed (off-by-one). This desynchronizes the BD
ring, which can corrupt DMA page reference counts and lead to SLUB
freelist corruption.

Commit 4e910dbe3650 ("qede: confirm skb is allocated before using")
added a NULL check inside qede_build_skb() to prevent a NULL pointer
dereference, but did not address the missing NULL checks in the
callers, making this off-by-one reachable.

Fix this by adding NULL checks for the return value of
qede_build_skb() in both qede_rx_build_skb() and
qede_tpa_rx_build_skb(), returning NULL immediately before any BD ring
manipulation.

## References
- https://git.kernel.org/stable/c/07be8b8adf91b7ada4c3dacce064d572a6066421
- https://git.kernel.org/stable/c/0bf78df2d3ecb1f4964ff42a7327d25845955153
- https://git.kernel.org/stable/c/1624aa100c0b218181aa74e3696a389b509298cb
- https://git.kernel.org/stable/c/814a5edac8c9fc04051808d5faaa93768e989281
- https://git.kernel.org/stable/c/982d6d6bc059c5dff37a2201c2f08c14bcfcbd20
- https://git.kernel.org/stable/c/a0a558ca7e75b49e71f8c545c30e8c005e6e4e2f
- https://git.kernel.org/stable/c/b066420e57f3402a52c998678b4678252ac9bb63
- https://git.kernel.org/stable/c/ecc05d4b20220a09c9c69584fc46ca55248a374a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72339.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72339
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
