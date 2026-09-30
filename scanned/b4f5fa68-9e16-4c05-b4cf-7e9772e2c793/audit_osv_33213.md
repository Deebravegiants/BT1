# [M] mm/userfaultfd: fix kmap_local LIFO ordering for CONFIG_HIGHPTE

## Summary
Severity: Medium
Advisory: CVE-2025-39899
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-10-01
Source: https://osv.dev/vulnerability/CVE-2025-39899
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.12.46, >=6.13.0 <6.16.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

mm/userfaultfd: fix kmap_local LIFO ordering for CONFIG_HIGHPTE

With CONFIG_HIGHPTE on 32-bit ARM, move_pages_pte() maps PTE pages using
kmap_local_page(), which requires unmapping in Last-In-First-Out order.

The current code maps dst_pte first, then src_pte, but unmaps them in the
same order (dst_pte, src_pte), violating the LIFO requirement.  This
causes the warning in kunmap_local_indexed():

  WARNING: CPU: 0 PID: 604 at mm/highmem.c:622 kunmap_local_indexed+0x178/0x17c
  addr \!= __fix_to_virt(FIX_KMAP_BEGIN + idx)

Fix this by reversing the unmap order to respect LIFO ordering.

This issue follows the same pattern as similar fixes:
- commit eca6828403b8 ("crypto: skcipher - fix mismatch between mapping and unmapping order")
- commit 8cf57c6df818 ("nilfs2: eliminate staggered calls to kunmap in nilfs_rename")

Both of which addressed the same fundamental requirement that kmap_local
operations must follow LIFO ordering.

## References
- https://git.kernel.org/stable/c/9614d8bee66387501f48718fa306e17f2aa3f2f3
- https://git.kernel.org/stable/c/b051f707018967ea8f697d790a1ed8c443f63812
- https://git.kernel.org/stable/c/bd1ee62759d0bd4d6b909731c076c230ac89d61e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39899.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39899
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
