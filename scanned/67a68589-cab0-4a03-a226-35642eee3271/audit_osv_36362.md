# [H] smb: client: split cached_fid bitfields to avoid shared-byte RMW races

## Summary
Severity: High
Advisory: CVE-2026-23230
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-02-18
Source: https://osv.dev/vulnerability/CVE-2026-23230
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.1.0 <6.1.164, >=6.2.0 <6.6.125, >=6.7.0 <6.12.72, >=6.13.0 <6.18.11, >=6.19.0 <6.19.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

smb: client: split cached_fid bitfields to avoid shared-byte RMW races

is_open, has_lease and on_list are stored in the same bitfield byte in
struct cached_fid but are updated in different code paths that may run
concurrently. Bitfield assignments generate byte read–modify–write
operations (e.g. `orb $mask, addr` on x86_64), so updating one flag can
restore stale values of the others.

A possible interleaving is:
    CPU1: load old byte (has_lease=1, on_list=1)
    CPU2: clear both flags (store 0)
    CPU1: RMW store (old | IS_OPEN) -> reintroduces cleared bits

To avoid this class of races, convert these flags to separate bool
fields.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-253495.html
- https://git.kernel.org/stable/c/3eaa22d688311c708b73f3c68bc6d0c8e3f0f77a
- https://git.kernel.org/stable/c/4386f6af8aaedd0c5ad6f659b40cadcc8f423828
- https://git.kernel.org/stable/c/4cfa4c37dcbcfd70866e856200ed8a2894cac578
- https://git.kernel.org/stable/c/569fecc56bfe4df66f05734d67daef887746656b
- https://git.kernel.org/stable/c/c4b9edd55987384a1f201d3d07ff71e448d79c1b
- https://git.kernel.org/stable/c/ec306600d5ba7148c9dbf8f5a8f1f5c1a044a241
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23230.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23230
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
