# [H] erofs: add GFP_NOIO in the bio completion if needed

## Summary
Severity: High
Advisory: CVE-2026-31467
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-22
Source: https://osv.dev/vulnerability/CVE-2026-31467
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.13.0 <5.15.203, >=5.16.0 <6.1.168, >=6.2.0 <6.6.131, >=6.7.0 <6.12.80, >=6.13.0 <6.18.21, >=6.19.0 <6.19.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

erofs: add GFP_NOIO in the bio completion if needed

The bio completion path in the process context (e.g. dm-verity)
will directly call into decompression rather than trigger another
workqueue context for minimal scheduling latencies, which can
then call vm_map_ram() with GFP_KERNEL.

Due to insufficient memory, vm_map_ram() may generate memory
swapping I/O, which can cause submit_bio_wait to deadlock
in some scenarios.

Trimmed down the call stack, as follows:

f2fs_submit_read_io
  submit_bio                      //bio_list is initialized.
    mmc_blk_mq_recovery
      z_erofs_endio
        vm_map_ram
          __pte_alloc_kernel
            __alloc_pages_direct_reclaim
              shrink_folio_list
                __swap_writepage
                  submit_bio_wait  //bio_list is non-NULL, hang!!!

Use memalloc_noio_{save,restore}() to wrap up this path.

## References
- https://git.kernel.org/stable/c/378949f46e897204384f3f5f91e42e93e3f87568
- https://git.kernel.org/stable/c/5c8ecdcfbfb0b0c6a82a4ebadc1ddea61609b902
- https://git.kernel.org/stable/c/c23df30915f83e7257c8625b690a1cece94142a0
- https://git.kernel.org/stable/c/d6565ea662e17d45a577184b0011bd69de22dc2b
- https://git.kernel.org/stable/c/d9d8360cb66e3b599d89d2526e7da8b530ebf2ff
- https://git.kernel.org/stable/c/da40464064599eefe78749f75cd2bba371044c04
- https://git.kernel.org/stable/c/e83e20b82859f0588e9a52a6fa9fea704a2061cf
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31467.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31467
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
