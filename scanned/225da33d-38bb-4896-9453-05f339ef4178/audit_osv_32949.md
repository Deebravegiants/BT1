# [H] nvmet: fix memory leak of bio integrity

## Summary
Severity: High
Advisory: CVE-2025-38405
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-07-25
Source: https://osv.dev/vulnerability/CVE-2025-38405
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.12.37, >=6.13.0 <6.15.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

nvmet: fix memory leak of bio integrity

If nvmet receives commands with metadata there is a continuous memory
leak of kmalloc-128 slab or more precisely bio->bi_integrity.

Since commit bf4c89fc8797 ("block: don't call bio_uninit from bio_endio")
each user of bio_init has to use bio_uninit as well. Otherwise the bio
integrity is not getting free. Nvmet uses bio_init for inline bios.

Uninit the inline bio to complete deallocation of integrity in bio.

## References
- https://git.kernel.org/stable/c/190f4c2c863af7cc5bb354b70e0805f06419c038
- https://git.kernel.org/stable/c/2e2028fcf924d1c6df017033c8d6e28b735a0508
- https://git.kernel.org/stable/c/431e58d56fcb5ff1f9eb630724a922e0d2a941df
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38405.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38405
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
