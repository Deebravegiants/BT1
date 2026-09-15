# [H] CVE-2022-28796

## Summary
Severity: High
Advisory: CVE-2022-28796
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-04-08
Source: https://osv.dev/vulnerability/CVE-2022-28796
Type: osv

## Details
jbd2_journal_wait_updates in fs/jbd2/transaction.c in the Linux kernel before 5.17.1 has a use-after-free caused by a transaction_t race condition.

## References
- https://security.netapp.com/advisory/ntap-20220506-0006/
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.17.1
- https://github.com/torvalds/linux/commit/cc16eecae687912238ee6efbff71ad31e2bc414e
