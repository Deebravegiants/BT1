# [H] wifi: ath12k: Correct tid cleanup when tid setup fails

## Summary
Severity: High
Advisory: CVE-2025-39750
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-11
Source: https://osv.dev/vulnerability/CVE-2025-39750
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.3.0 <6.6.103, >=6.7.0 <6.12.43, >=6.13.0 <6.15.11, >=6.16.0 <6.16.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: ath12k: Correct tid cleanup when tid setup fails

Currently, if any error occurs during ath12k_dp_rx_peer_tid_setup(),
the tid value is already incremented, even though the corresponding
TID is not actually allocated. Proceed to
ath12k_dp_rx_peer_tid_delete() starting from unallocated tid,
which might leads to freeing unallocated TID and cause potential
crash or out-of-bounds access.

Hence, fix by correctly decrementing tid before cleanup to match only
the successfully allocated TIDs.

Also, remove tid-- from failure case of ath12k_dp_rx_peer_frag_setup(),
as decrementing the tid before cleanup in loop will take care of this.

Compile tested only.

## References
- https://git.kernel.org/stable/c/2ef17d1476ab26bce89764e2f16833d7f52acc38
- https://git.kernel.org/stable/c/30cad87978057516c93467516bc481a3eacfd66a
- https://git.kernel.org/stable/c/4a2bf707270f897ab8077baee8ed5842a5321686
- https://git.kernel.org/stable/c/6301fe4f209165334d251a1c6da8ae47f93cb32c
- https://git.kernel.org/stable/c/907c630e58af9e86e215f3951c7b287bd86d0f15
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39750.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39750
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
