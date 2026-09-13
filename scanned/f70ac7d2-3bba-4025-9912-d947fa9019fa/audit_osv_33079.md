# [H] net: kcm: Fix race condition in kcm_unattach()

## Summary
Severity: High
Advisory: CVE-2025-38717
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-04
Source: https://osv.dev/vulnerability/CVE-2025-38717
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.6.0 <6.12.43, >=6.13.0 <6.15.11, >=6.16.0 <6.16.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: kcm: Fix race condition in kcm_unattach()

syzbot found a race condition when kcm_unattach(psock)
and kcm_release(kcm) are executed at the same time.

kcm_unattach() is missing a check of the flag
kcm->tx_stopped before calling queue_work().

If the kcm has a reserved psock, kcm_unattach() might get executed
between cancel_work_sync() and unreserve_psock() in kcm_release(),
requeuing kcm->tx_work right before kcm gets freed in kcm_done().

Remove kcm->tx_stopped and replace it by the less
error-prone disable_work_sync().

## References
- https://git.kernel.org/stable/c/52565a935213cd6a8662ddb8efe5b4219343a25d
- https://git.kernel.org/stable/c/7275dc3bb8f91b23125ff3f47b6529935cf46152
- https://git.kernel.org/stable/c/798733ee5d5788b12e8a52db1519abc17e826f69
- https://git.kernel.org/stable/c/c0bffbc92a1ca3960fb9cdb8e9f75a68468eb308
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38717.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38717
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
