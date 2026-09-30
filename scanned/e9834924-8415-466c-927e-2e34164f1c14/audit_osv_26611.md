# [H] mlx5: fix possible ptp queue fifo use-after-free

## Summary
Severity: High
Advisory: CVE-2023-53398
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-18
Source: https://osv.dev/vulnerability/CVE-2023-53398
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <6.1.18, >=6.2.0 <6.2.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

mlx5: fix possible ptp queue fifo use-after-free

Fifo indexes are not checked during pop operations and it leads to
potential use-after-free when poping from empty queue. Such case was
possible during re-sync action. WARN_ON_ONCE covers future cases.

There were out-of-order cqe spotted which lead to drain of the queue and
use-after-free because of lack of fifo pointers check. Special check and
counter are added to avoid resync operation if SKB could not exist in the
fifo because of OOO cqe (skb_id must be between consumer and producer
index).

## References
- https://git.kernel.org/stable/c/3a50cf1e8e5157b82268eee7e330dbe5736a0948
- https://git.kernel.org/stable/c/52e6e7a0bc04c85012a9251c7cf2d444a77eb966
- https://git.kernel.org/stable/c/6afdedc4e66e3846ce497744f01b95c34bf39d21
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53398.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53398
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
