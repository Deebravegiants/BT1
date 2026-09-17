# [H] RDMA/bnxt_re: Fix OOB write in bnxt_re_copy_err_stats()

## Summary
Severity: High
Advisory: CVE-2025-71092
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-01-13
Source: https://osv.dev/vulnerability/CVE-2025-71092
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.18.0 <6.18.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/bnxt_re: Fix OOB write in bnxt_re_copy_err_stats()

Commit ef56081d1864 ("RDMA/bnxt_re: RoCE related hardware counters
update") added three new counters and placed them after
BNXT_RE_OUT_OF_SEQ_ERR.

BNXT_RE_OUT_OF_SEQ_ERR acts as a boundary marker for allocating hardware
statistics with different num_counters values on chip_gen_p5_p7 devices.

As a result, BNXT_RE_NUM_STD_COUNTERS are used when allocating
hw_stats, which leads to an out-of-bounds write in
bnxt_re_copy_err_stats().

The counters BNXT_RE_REQ_CQE_ERROR, BNXT_RE_RESP_CQE_ERROR, and
BNXT_RE_RESP_REMOTE_ACCESS_ERRS are applicable to generic hardware, not
only p5/p7 devices.

Fix this by moving these counters before BNXT_RE_OUT_OF_SEQ_ERR so they
are included in the generic counter set.

## References
- https://git.kernel.org/stable/c/369a161c48723f60f06f3510b82ea7d96d0499ab
- https://git.kernel.org/stable/c/9b68a1cc966bc947d00e4c0df7722d118125aa37
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/71xxx/CVE-2025-71092.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-71092
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
