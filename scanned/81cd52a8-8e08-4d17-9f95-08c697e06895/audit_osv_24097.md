# [H] RDMA/irdma: Fix a window for use-after-free

## Summary
Severity: High
Advisory: CVE-2022-50137
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-06-18
Source: https://osv.dev/vulnerability/CVE-2022-50137
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.14.0 <5.15.61, >=5.16.0 <5.18.18, >=5.19.0 <5.19.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/irdma: Fix a window for use-after-free

During a destroy CQ an interrupt may cause processing of a CQE after CQ
resources are freed by irdma_cq_free_rsrc(). Fix this by moving the call
to irdma_cq_free_rsrc() after the irdma_sc_cleanup_ceqes(), which is
called under the cq_lock.

## References
- https://git.kernel.org/stable/c/0abf2eef80295923b819ce89ff9edc1fe61be17c
- https://git.kernel.org/stable/c/350ac793a03c8a30a3f2b27fc282cd1c67070763
- https://git.kernel.org/stable/c/8ecef7890b3aea78c8bbb501a4b5b8134367b821
- https://git.kernel.org/stable/c/92520864ef9f912f38b403d172a0ded020683d55
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50137.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50137
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
