# [H] mptcp: reclaim forward-allocated memory on RX path errors

## Summary
Severity: High
Advisory: CVE-2026-80588
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-80588
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.18.46, >=6.19.0 <7.1.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

mptcp: reclaim forward-allocated memory on RX path errors

After commit 9db5b3cec4ec ("mptcp: borrow forward memory from subflow"),
errors in the receive path prior to queueing skbs into the receive
queue do not trigger forward-allocated memory reclaiming.

Prevent forward memory from growing unboundedly in pathological drop
scenarios by explicitly reclaiming memory when skbs are dropped.

## References
- https://git.kernel.org/stable/c/41b49a8b914ec7dcb03eae93fb27f3c464078644
- https://git.kernel.org/stable/c/473f1a5ab2abc98dd9e74b95b9c23c66c47535cc
- https://git.kernel.org/stable/c/8277f48a06d3aa1441f6d0b6998ccc0360d30ed8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80588.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80588
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
