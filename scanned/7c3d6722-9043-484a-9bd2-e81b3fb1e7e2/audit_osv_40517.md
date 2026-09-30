# [C] nfsd: release layout stid on setlease failure

## Summary
Severity: Critical
Advisory: CVE-2026-53399
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-53399
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.0.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.96, >=6.13.0 <6.18.39, >=6.19.0 <7.1.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

nfsd: release layout stid on setlease failure

nfs4_alloc_stid() publishes the new stid into cl->cl_stateids via
idr_alloc_cyclic() under cl_lock before returning to
nfsd4_alloc_layout_stateid(). When nfsd4_layout_setlease() then
fails, the error path frees the layout stateid directly with
kmem_cache_free() without ever calling idr_remove(), leaving the
IDR slot pointing at freed slab memory. Any subsequent IDR walker
(states_show, client teardown) dereferences the dangling pointer.

The correct teardown for an IDR-published stid is nfs4_put_stid(),
which removes the IDR slot under cl_lock, dispatches sc_free
(nfsd4_free_layout_stateid) to release ls->ls_file via
nfsd4_close_layout(), and drops the nfs4_file reference in its
tail.

A second issue blocks that switch: nfsd4_free_layout_stateid()
unconditionally inspects ls->ls_fence_work via
delayed_work_pending() under ls_lock, but
INIT_DELAYED_WORK(&ls->ls_fence_work, ...) currently runs only
after the setlease call. On the setlease-failure path the
destructor would touch an uninitialized delayed_work.

    nfsd4_alloc_layout_stateid()
      nfs4_alloc_stid()           /* idr_alloc_cyclic under cl_lock */
      nfsd4_layout_setlease()     /* fails */
        nfs4_put_stid()
          nfsd4_free_layout_stateid()
            delayed_work_pending(&ls->ls_fence_work)  /* needs INIT */
            nfsd4_close_layout()  /* nfsd_file_put(ls->ls_file) */
          put_nfs4_file()

Fix by hoisting the ls_fenced / ls_fence_delay / INIT_DELAYED_WORK
initialization above the nfsd4_layout_setlease() call, and replace
the manual nfsd_file_put + put_nfs4_file + kmem_cache_free cleanup
with a single nfs4_put_stid(stp).

## References
- https://git.kernel.org/stable/c/2e0a5d6d62600b8c614d1b55e50ef94035d6adf9
- https://git.kernel.org/stable/c/30d55c8aabb261bc3f427d6b9aae7ef6206063f9
- https://git.kernel.org/stable/c/48a586e382e4db1dbf958d44b63e081df5f8ed04
- https://git.kernel.org/stable/c/7bbb7ce74051c8be4b69ff44ce3db370600dae61
- https://git.kernel.org/stable/c/83c2b7797742339bb768f83935f7ca33950db138
- https://git.kernel.org/stable/c/8dee7c278f1c2b5bb80e17a6281c3812fc8b0cdd
- https://git.kernel.org/stable/c/d369e5edfaaf83a448016e2f1da392b2174be801
- https://git.kernel.org/stable/c/d788ef40a7517d22c97ab01700e4ae4c611b6f2f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53399.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53399
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
