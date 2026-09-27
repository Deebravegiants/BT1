# [H] RDMA/bnxt_re: zero shared page before exposing to userspace

## Summary
Severity: High
Advisory: CVE-2026-74584
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-74584
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.11.0 <5.10.260, >=5.11.0 <5.15.211, >=5.16.0 <6.1.177, >=6.2.0 <6.6.144, >=6.7.0 <6.12.95, >=6.13.0 <6.18.37, >=6.19.0 <7.0.14

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/bnxt_re: zero shared page before exposing to userspace

bnxt_re_alloc_ucontext() allocates uctx->shpg via
__get_free_page(GFP_KERNEL). The buddy allocator does not zero pages
without __GFP_ZERO, so the page contains stale kernel data from
whatever object most recently freed it.

The page is then mapped into userspace via vm_insert_page() under
BNXT_RE_MMAP_SH_PAGE in bnxt_re_mmap(). The driver only ever writes
4 bytes (a u32 AVID) at offset BNXT_RE_AVID_OFFT (0x10) inside
bnxt_re_create_ah(); the remaining 4092 bytes of the page are exposed
to userspace unsanitised, leaking kernel memory contents.

Any user with access to /dev/infiniband/uverbsX on a host with a
bnxt_re device (typically rdma group membership) can read this data
via a single mmap() at pgoff 0 after IB_USER_VERBS_CMD_GET_CONTEXT.

Other shared pages in the same file already use get_zeroed_page()
correctly:

  drivers/infiniband/hw/bnxt_re/ib_verbs.c
      srq->uctx_srq_page = (void *)get_zeroed_page(GFP_KERNEL);
      cq->uctx_cq_page  = (void *)get_zeroed_page(GFP_KERNEL);

uctx->shpg is the only outlier. Bring it in line with the existing
convention by switching to get_zeroed_page().

## References
- https://git.kernel.org/stable/c/53c97e9882f4e747b4ac31b211317c2eba541af9
- https://git.kernel.org/stable/c/9128c2411b83a64c0a69d2ff059c741bde25a9cc
- https://git.kernel.org/stable/c/9896bdfd21d918e9f26a52bc6109cc77970ee0b1
- https://git.kernel.org/stable/c/a3ed2daab02b2a706e882ad31b5c3c4f33cb5bb1
- https://git.kernel.org/stable/c/c19b360fa10c521c0b681875cdaa51545d45a491
- https://git.kernel.org/stable/c/c75f8ce4baa29ae57fe615c6a2c5101f59b8b89a
- https://git.kernel.org/stable/c/e2b143df29003d2704b51f62e9297006953dbacb
- https://git.kernel.org/stable/c/f6b079629becfa977f9c51fe53ad2e6dcc55ef44
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74584.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74584
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
