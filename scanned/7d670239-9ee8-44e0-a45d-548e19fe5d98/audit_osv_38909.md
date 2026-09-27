# [H] crypto: caam - fix DMA corruption on long hmac keys

## Summary
Severity: High
Advisory: CVE-2026-43044
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-01
Source: https://osv.dev/vulnerability/CVE-2026-43044
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.3.0 <6.6.134, >=6.7.0 <6.12.81, >=6.13.0 <6.18.22, >=6.19.0 <6.19.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

crypto: caam - fix DMA corruption on long hmac keys

When a key longer than block size is supplied, it is copied and then
hashed into the real key.  The memory allocated for the copy needs to
be rounded to DMA cache alignment, as otherwise the hashed key may
corrupt neighbouring memory.

The rounding was performed, but never actually used for the allocation.
Fix this by replacing kmemdup with kmalloc for a larger buffer,
followed by memcpy.

## References
- https://git.kernel.org/stable/c/5ddfdcbe10dc5f97afc4e46ca22be2be717e8caf
- https://git.kernel.org/stable/c/68feed135a0c7243a9275ae7e6a18260f755f52b
- https://git.kernel.org/stable/c/a7ecf06d3ee06e9b3322e1e7b003ea5c6f6e135a
- https://git.kernel.org/stable/c/c0c133e0225d87aad326bb90bbce9bdd6fde3cbb
- https://git.kernel.org/stable/c/f2af8be110bde26b3e3354efdfdda97f426306a4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43044.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43044
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
