# [M] drm/panthor: Be stricter about IO mapping flags

## Summary
Severity: Medium
Advisory: CVE-2024-53071
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-19
Source: https://osv.dev/vulnerability/CVE-2024-53071
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.11.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/panthor: Be stricter about IO mapping flags

The current panthor_device_mmap_io() implementation has two issues:

1. For mapping DRM_PANTHOR_USER_FLUSH_ID_MMIO_OFFSET,
   panthor_device_mmap_io() bails if VM_WRITE is set, but does not clear
   VM_MAYWRITE. That means userspace can use mprotect() to make the mapping
   writable later on. This is a classic Linux driver gotcha.
   I don't think this actually has any impact in practice:
   When the GPU is powered, writes to the FLUSH_ID seem to be ignored; and
   when the GPU is not powered, the dummy_latest_flush page provided by the
   driver is deliberately designed to not do any flushes, so the only thing
   writing to the dummy_latest_flush could achieve would be to make *more*
   flushes happen.

2. panthor_device_mmap_io() does not block MAP_PRIVATE mappings (which are
   mappings without the VM_SHARED flag).
   MAP_PRIVATE in combination with VM_MAYWRITE indicates that the VMA has
   copy-on-write semantics, which for VM_PFNMAP are semi-supported but
   fairly cursed.
   In particular, in such a mapping, the driver can only install PTEs
   during mmap() by calling remap_pfn_range() (because remap_pfn_range()
   wants to **store the physical address of the mapped physical memory into
   the vm_pgoff of the VMA**); installing PTEs later on with a fault
   handler (as panthor does) is not supported in private mappings, and so
   if you try to fault in such a mapping, vmf_insert_pfn_prot() splats when
   it hits a BUG() check.

Fix it by clearing the VM_MAYWRITE flag (userspace writing to the FLUSH_ID
doesn't make sense) and requiring VM_SHARED (copy-on-write semantics for
the FLUSH_ID don't make sense).

Reproducers for both scenarios are in the notes of my patch on the mailing
list; I tested that these bugs exist on a Rock 5B machine.

Note that I only compile-tested the patch, I haven't tested it; I don't
have a working kernel build setup for the test machine yet. Please test it
before applying it.

## References
- https://git.kernel.org/stable/c/2604afd65043e8f9d4be036cb1242adf6b5723cf
- https://git.kernel.org/stable/c/f432a1621f049bb207e78363d9d0e3c6fa2da5db
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53071.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53071
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
