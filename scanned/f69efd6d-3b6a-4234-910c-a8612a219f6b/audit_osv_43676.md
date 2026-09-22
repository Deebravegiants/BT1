# [C] KVM: arm64: vgic: Fix race between LPI release and re-registration

## Summary
Severity: Critical
Advisory: CVE-2026-74568
Ecosystem: Linux
CVSS: 9.3 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74568
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.17.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

KVM: arm64: vgic: Fix race between LPI release and re-registration

Fix a potential race between decrementing an LPI's reference count and
evicting that structure from the LPI xarray.

LPI structures are maintained in the VGIC LPI xarray (dist->lpi_xa).
When the reference count of an LPI structure drops to zero,
vgic_release_lpi_locked() removes the structure from the xarray and
frees it under the xarray lock.

However, the release of an LPI can race with a concurrent LPI
re-registration with the same INTID via vgic_add_lpi() on another CPU,
since the reference count drop and the xarray eviction are not performed
in a single atomic step. This can happen e.g. if the guest issues a
DISCARD while the LPI is still referenced from a vCPU's active-pending
list (ap_list), and the same INTID is re-mapped via MAPTI.

Particularly, vgic_release_lpi_locked() is called from two distinct
paths: direct release via vgic_put_irq(), and deferred release via
vgic_release_deleted_lpis(). During direct release, the issue can result
in deleting a newly registered LPI from the xarray:

  CPU0 (Releasing LPI)                    CPU1 (Adding new LPI)
  ====================                    =====================
  vgic_put_irq()
      __vgic_put_irq()
          refcount_dec_and_test()
                                          vgic_add_lpi()
                                              xa_lock_irqsave()
                                              old_irq = xa_load(.., intid)
                                              vgic_try_get_irq_ref(old_irq) == false
                        new IRQ inserted -->  __xa_store(.., intid, ..)
                                              xa_unlock_irqrestore()
  xa_lock_irqsave();
  vgic_release_lpi_locked()
      __xa_erase(.., irq->intid)   <-- BUG: new IRQ is erased
      kfree_rcu(old_irq)

During the deferred release path, the old IRQ can be leaked:

  CPU0 (Releasing LPI)                    CPU1 (Adding new LPI)
  ====================                    =====================
  vgic_put_irq_norelease()
      __vgic_put_irq()
          refcount_dec_and_test()
      irq->pending_release = true
                                          vgic_add_lpi()
                                              xa_lock_irqsave()
                                              old_irq = xa_load(.., intid)
                                              vgic_try_get_irq_ref(oldirq) == false
                 BUG: old IRQ overwritten --> __xa_store(.., intid, ..)
                                              xa_unlock_irqrestore()

  vgic_release_deleted_lpis()
      xa_lock_irqsave()
      xa_for_each() { .. } <-- old IRQ with pending_release = true
                               is gone, so it cannot be released

To fix the direct release path, move the reference count drop inside
the xarray lock, making sure that vgic_add_lpi() never encounters the
to-be-released LPI.

In the deferred release path, the refcount drop must happen under a raw
spinlock, so the xarray lock cannot be grabbed, and the same solution
does not work. Instead, update vgic_add_lpi(), so that if it evicts
an LPI from the xarray, it takes on the responsibility of freeing it.
Consequently, an LPI may now be freed concurrently after a deferred
release drops the refcount, so accessing the pending_release field is no
longer safe from use-after-free. Delete all uses of the flag, and update
vgic_release_deleted_lpis() to identify orphaned LPIs purely based on
their refcount.

## References
- https://git.kernel.org/stable/c/292e80a159aa88635bf668a7212cfdf526b8bd52
- https://git.kernel.org/stable/c/cbfe2b24a1ea9de35032dbdd100fdc700f5be92d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74568.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74568
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
