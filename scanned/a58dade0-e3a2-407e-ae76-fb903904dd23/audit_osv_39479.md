# [H] RDMA/uverbs: Validate wqe_size before using it in ib_uverbs_post_send

## Summary
Severity: High
Advisory: CVE-2026-45856
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2026-45856
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.0.0 <5.10.252, >=5.11.0 <5.15.202, >=5.16.0 <6.1.165, >=6.2.0 <6.6.128, >=6.7.0 <6.12.75, >=6.13.0 <6.18.14, >=6.19.0 <6.19.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/uverbs: Validate wqe_size before using it in ib_uverbs_post_send

ib_uverbs_post_send() uses cmd.wqe_size from userspace without any
validation before passing it to kmalloc() and using the allocated
buffer as struct ib_uverbs_send_wr.

If a user provides a small wqe_size value (e.g., 1), kmalloc() will
succeed, but subsequent accesses to user_wr->opcode, user_wr->num_sge,
and other fields will read beyond the allocated buffer, resulting in
an out-of-bounds read from kernel heap memory. This could potentially
leak sensitive kernel information to userspace.

Additionally, providing an excessively large wqe_size can trigger a
WARNING in the memory allocation path, as reported by syzkaller.

This is inconsistent with ib_uverbs_unmarshall_recv() which properly
validates that wqe_size >= sizeof(struct ib_uverbs_recv_wr) before
proceeding.

Add the same validation for ib_uverbs_post_send() to ensure wqe_size
is at least sizeof(struct ib_uverbs_send_wr).

## References
- https://git.kernel.org/stable/c/01c9b152647dc70dc06a4a2eff86ebb3b3c76075
- https://git.kernel.org/stable/c/1956f0a74ccf5dc9c3ef717f2985c3ed3400aab0
- https://git.kernel.org/stable/c/9b5ac1c15334d46c0dbd49d64a2257b929500163
- https://git.kernel.org/stable/c/9c15ec4cd4e7f57c6bbcb4e73e99290f150dd2a7
- https://git.kernel.org/stable/c/bef70ff9841990658610512b4a18e4a88c9b4df6
- https://git.kernel.org/stable/c/bf1feed1a7886af945f92890493aefd2b5c9928a
- https://git.kernel.org/stable/c/bf4454da8b1e712714628c0a0d6e7845bb40790a
- https://git.kernel.org/stable/c/d533425ac1f2925b4fc3e4ed9b9d72362cb23475
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45856.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-45856
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
