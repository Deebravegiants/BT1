# [H] misc: fastrpc: fix use-after-free of fastrpc_user in workqueue context

## Summary
Severity: High
Advisory: CVE-2026-53161
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-53161
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.1.0 <5.10.259, >=5.11.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.94, >=6.13.0 <6.18.36, >=6.19.0 <7.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

misc: fastrpc: fix use-after-free of fastrpc_user in workqueue context

There is a race between fastrpc_device_release() and the workqueue
that processes DSP responses. When the user closes the file descriptor,
fastrpc_device_release() frees the fastrpc_user structure. Concurrently,
an in-flight DSP invocation can complete and fastrpc_rpmsg_callback()
schedules context cleanup via schedule_work(&ctx->put_work). If the
workqueue runs fastrpc_context_free() in parallel with or after
fastrpc_device_release() has freed the user structure, it dereferences
the freed fastrpc_user. Depending on the state of the context at the
time of the race, any one of the following accesses can be hit:

 1. fastrpc_buf_free() calls fastrpc_ipa_to_dma_addr(buf->fl->cctx, ...)
    to strip the SID bits from the stored IOVA before passing the
    physical address to dma_free_coherent().

 2. fastrpc_free_map() reads map->fl->cctx->vmperms[0].vmid to
    reconstruct the source permission bitmask needed for the
    qcom_scm_assign_mem() call that returns memory from the DSP VM
    back to HLOS.

 3. fastrpc_free_map() acquires map->fl->lock to safely remove the
    map node from the fl->maps list.

The resulting use-after-free manifests as:

  pc : fastrpc_buf_free+0x38/0x80 [fastrpc]
  lr : fastrpc_context_free+0xa8/0x1b0 [fastrpc]
  fastrpc_context_free+0xa8/0x1b0 [fastrpc]
  fastrpc_context_put_wq+0x78/0xa0 [fastrpc]
  process_one_work+0x180/0x450
  worker_thread+0x26c/0x388

Add kref-based reference counting to fastrpc_user. Have each invoke
context take a reference on the user at allocation time and release it
when the context is freed. Release the initial reference in
fastrpc_device_release() at file close. Move the teardown of the user
structure — freeing pending contexts, maps, mmaps, and the channel
context reference — into the kref release callback fastrpc_user_free(),
so that it runs only when the last reference is dropped, regardless of
whether that happens at device close or after the final in-flight
context completes.

## References
- https://git.kernel.org/stable/c/5278ccd357e0d7aeeb1e76c0f3e0e02894a9897c
- https://git.kernel.org/stable/c/c6e5c2be09f814377d7f1ce97370a5b7b3e02814
- https://git.kernel.org/stable/c/d42679eef34dd590b694ce3b666c5e2ba10cd4bf
- https://git.kernel.org/stable/c/df08fadcf0e5f3708365ec3b6d30b5aafd98bea1
- https://git.kernel.org/stable/c/e1e3a05efe5954d5bad01157d79429d39a67a7ae
- https://git.kernel.org/stable/c/e85eb5feca8e254905ffa6c57a3c99c89a674a0f
- https://git.kernel.org/stable/c/ecea4967c2bff92c2fafbc59893f711b39f7b152
- https://git.kernel.org/stable/c/fbe0947420eec18a84638d29468c2d563ce4e6a3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53161.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53161
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
