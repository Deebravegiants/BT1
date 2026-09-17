# [H] RDMA/rxe: Copy WQE to local buffer in non-SRQ receive path

## Summary
Severity: High
Advisory: CVE-2026-74377
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74377
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.8.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/rxe: Copy WQE to local buffer in non-SRQ receive path

For non-SRQ QPs, the responder reads WQE fields directly from the
shared queue buffer mapped into userspace. This allows a malicious
user to modify fields like num_sge or sge entries while the kernel
is processing the WQE, leading to out-of-bounds reads in
rxe_resp_check_length() and copy_data().

Introduce get_recv_wqe() that validates num_sge and copies the WQE
to a kernel-local buffer before processing, matching the approach
already used for SRQ WQEs in get_srq_wqe(). The srq_wqe buffer is
reused since SRQ and non-SRQ paths are mutually exclusive per QP.

## References
- https://git.kernel.org/stable/c/2e60378fb3c8b51c94103bb40014c4fe38fa5033
- https://git.kernel.org/stable/c/5420eebf3b3c162bfaf965f30e61cd1d689e5732
- https://git.kernel.org/stable/c/9fa785137303f7109c23dea779b8dedc67c9b531
- https://git.kernel.org/stable/c/a211b7904aed365e4e4f08a48ec6e6dd1ea7b16b
- https://git.kernel.org/stable/c/d6ab440240a04b8737ee4c7bb21af9182e451733
- https://git.kernel.org/stable/c/fc72fd61cc8b2e2e3e92ae4c0e9cc30c9a7ecb78
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74377.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74377
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
