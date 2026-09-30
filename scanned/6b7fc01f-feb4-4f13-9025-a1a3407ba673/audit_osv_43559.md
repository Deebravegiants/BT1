# [H] RDMA/rxe: Fix TOCTOU heap overflow in get_srq_wqe

## Summary
Severity: High
Advisory: CVE-2026-74378
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74378
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.8.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/rxe: Fix TOCTOU heap overflow in get_srq_wqe

get_srq_wqe() reads wqe->dma.num_sge from the shared receive queue
buffer, which is mapped into userspace. It validates num_sge against
max_sge, but then re-reads the same field to calculate the memcpy
size. A concurrent userspace thread can modify num_sge between
validation and use, causing a heap buffer overflow when copying the
WQE into qp->resp.srq_wqe.

Read num_sge into a local variable and use it for both the bounds
check and the size calculation.

## References
- https://git.kernel.org/stable/c/02558c86b6b761063e9399e6b939984500327ef1
- https://git.kernel.org/stable/c/22b8fbded65b8c441b634a185f8da67657df6c50
- https://git.kernel.org/stable/c/3cfa2a3adc51b7c57729961a03446962ff10e3d2
- https://git.kernel.org/stable/c/3e07ea9579dc9553d2285c26c2823931358aa3b8
- https://git.kernel.org/stable/c/b9800d7953d119bcc068c74587d48e4ba0313629
- https://git.kernel.org/stable/c/cd19a6345e3727adafafa5954b58b13c92e13b80
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74378.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74378
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
