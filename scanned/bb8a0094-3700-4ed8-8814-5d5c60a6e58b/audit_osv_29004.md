# [H] drivers/virt/acrn: fix PFNMAP PTE checks in acrn_vm_ram_map()

## Summary
Severity: High
Advisory: CVE-2024-38610
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-06-19
Source: https://osv.dev/vulnerability/CVE-2024-38610
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.15.161, >=5.16.0 <6.1.93, >=5.18.0 <6.6.33, >=6.2.0 <6.8.12, >=6.7.0 <6.9.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

drivers/virt/acrn: fix PFNMAP PTE checks in acrn_vm_ram_map()

Patch series "mm: follow_pte() improvements and acrn follow_pte() fixes".

Patch #1 fixes a bunch of issues I spotted in the acrn driver.  It
compiles, that's all I know.  I'll appreciate some review and testing from
acrn folks.

Patch #2+#3 improve follow_pte(), passing a VMA instead of the MM, adding
more sanity checks, and improving the documentation.  Gave it a quick test
on x86-64 using VM_PAT that ends up using follow_pte().


This patch (of 3):

We currently miss handling various cases, resulting in a dangerous
follow_pte() (previously follow_pfn()) usage.

(1) We're not checking PTE write permissions.

Maybe we should simply always require pte_write() like we do for
pin_user_pages_fast(FOLL_WRITE)? Hard to tell, so let's check for
ACRN_MEM_ACCESS_WRITE for now.

(2) We're not rejecting refcounted pages.

As we are not using MMU notifiers, messing with refcounted pages is
dangerous and can result in use-after-free. Let's make sure to reject them.

(3) We are only looking at the first PTE of a bigger range.

We only lookup a single PTE, but memmap->len may span a larger area.
Let's loop over all involved PTEs and make sure the PFN range is
actually contiguous. Reject everything else: it couldn't have worked
either way, and rather made use access PFNs we shouldn't be accessing.

## References
- https://git.kernel.org/stable/c/2c8d6e24930b8ef7d4a81787627c559ae0e0d3bb
- https://git.kernel.org/stable/c/3d6586008f7b638f91f3332602592caa8b00b559
- https://git.kernel.org/stable/c/4c4ba3cf3a15ccfbaf787d0296fa42cdb00da9b4
- https://git.kernel.org/stable/c/5c6705aa47b5b78d7ad36fea832bb69caa5bf49a
- https://git.kernel.org/stable/c/afeb0e69627695f759fc73c39c1640dbf8649b32
- https://git.kernel.org/stable/c/e873f36ec890bece26ecce850e969917bceebbb6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/38xxx/CVE-2024-38610.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-38610
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
