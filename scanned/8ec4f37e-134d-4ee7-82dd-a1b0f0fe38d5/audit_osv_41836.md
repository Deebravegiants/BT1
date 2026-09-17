# [H] mm/vmalloc: do not trigger BUG() on BH disabled context

## Summary
Severity: High
Advisory: CVE-2026-63955
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63955
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.19.0 <7.0.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

mm/vmalloc: do not trigger BUG() on BH disabled context

__get_vm_area_node() currently triggers a BUG() if in_interrupt() returns
true.  However, in_interrupt() also reports true when BH are disabled.

The bridge code can call rhashtable_lookup_insert_fast() with bottom
halves disabled:

__vlan_add()
 -> br_fdb_add_local()
  spin_lock_bh(&br->hash_lock); <-- Disable BH
   -> fdb_add_local()
    -> fdb_create()
     -> rhashtable_lookup_insert_fast()
      -> kvmalloc()
       -> vmalloc()
        -> __get_vm_area_node()
         -> BUG_ON(in_interrupt())
  spin_unlock_bh(&br->hash_lock)

this triggers the BUG() despite the caller not being in NMI or
hard IRQ context.

Replace the in_interrupt() check with in_nmi() || in_hardirq().

## References
- https://git.kernel.org/stable/c/04aa71da5f35aacdc9ae9cb5150947daa624f641
- https://git.kernel.org/stable/c/ad7eff07b625f53c3fb513b30d7a8c5a79fbc7ce
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63955.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63955
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
