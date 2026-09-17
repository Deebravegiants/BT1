# [H] mtd: spi-nor: debugfs: fix out-of-bounds read in spi_nor_params_show()

## Summary
Severity: High
Advisory: CVE-2026-46190
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-05-28
Source: https://osv.dev/vulnerability/CVE-2026-46190
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.19.0 <6.1.176, >=6.2.0 <6.6.140, >=6.7.0 <6.12.88, >=6.13.0 <6.18.30, >=6.19.0 <7.0.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

mtd: spi-nor: debugfs: fix out-of-bounds read in spi_nor_params_show()

Sashiko noticed an out-of-bounds read [1].

In spi_nor_params_show(), the snor_f_names array is passed to
spi_nor_print_flags() using sizeof(snor_f_names).

Since snor_f_names is an array of pointers, sizeof() returns the total
number of bytes occupied by the pointers
	(element_count * sizeof(void *))
rather than the element count itself. On 64-bit systems, this makes the
passed length 8x larger than intended.

Inside spi_nor_print_flags(), the 'names_len' argument is used to
bounds-check the 'names' array access. An out-of-bounds read occurs
if a flag bit is set that exceeds the array's actual element count
but is within the inflated byte-size count.

Correct this by using ARRAY_SIZE() to pass the actual number of
string pointers in the array.

## References
- https://git.kernel.org/stable/c/231b8e1f604f6e0a7e100536f506cdf482e2c5f5
- https://git.kernel.org/stable/c/34bdcfb496b29f9a52431194f94473b37fb8c162
- https://git.kernel.org/stable/c/9a80c458320e0514e11945402dd6e48fcee05524
- https://git.kernel.org/stable/c/c0b654bc0b76a1da102d9138be1ed1223bd99310
- https://git.kernel.org/stable/c/ca18c180b053f6ce80394322b314ac721c316af7
- https://git.kernel.org/stable/c/e47029b977e747cb3a9174308fd55762cce70147
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46190.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46190
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
