# [H] powerpc/kasan: Fix addr error caused by page alignment

## Summary
Severity: High
Advisory: CVE-2024-26712
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-04-03
Source: https://osv.dev/vulnerability/CVE-2024-26712
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.4.0 <5.10.210, >=5.11.0 <5.15.149, >=5.16.0 <6.1.79, >=6.2.0 <6.6.18, >=6.7.0 <6.7.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

powerpc/kasan: Fix addr error caused by page alignment

In kasan_init_region, when k_start is not page aligned, at the begin of
for loop, k_cur = k_start & PAGE_MASK is less than k_start, and then
`va = block + k_cur - k_start` is less than block, the addr va is invalid,
because the memory address space from va to block is not alloced by
memblock_alloc, which will not be reserved by memblock_reserve later, it
will be used by other places.

As a result, memory overwriting occurs.

for example:
int __init __weak kasan_init_region(void *start, size_t size)
{
[...]
	/* if say block(dcd97000) k_start(feef7400) k_end(feeff3fe) */
	block = memblock_alloc(k_end - k_start, PAGE_SIZE);
	[...]
	for (k_cur = k_start & PAGE_MASK; k_cur < k_end; k_cur += PAGE_SIZE) {
		/* at the begin of for loop
		 * block(dcd97000) va(dcd96c00) k_cur(feef7000) k_start(feef7400)
		 * va(dcd96c00) is less than block(dcd97000), va is invalid
		 */
		void *va = block + k_cur - k_start;
		[...]
	}
[...]
}

Therefore, page alignment is performed on k_start before
memblock_alloc() to ensure the validity of the VA address.

## References
- https://git.kernel.org/stable/c/0516c06b19dc64807c10e01bb99b552bdf2d7dbe
- https://git.kernel.org/stable/c/0c09912dd8387e228afcc5e34ac5d79b1e3a1058
- https://git.kernel.org/stable/c/230e89b5ad0a33f530a2a976b3e5e4385cb27882
- https://git.kernel.org/stable/c/2738e0aa2fb24a7ab9c878d912dc2b239738c6c6
- https://git.kernel.org/stable/c/4a7aee96200ad281a5cc4cf5c7a2e2a49d2b97b0
- https://git.kernel.org/stable/c/70ef2ba1f4286b2b73675aeb424b590c92d57b25
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26712.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26712
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
