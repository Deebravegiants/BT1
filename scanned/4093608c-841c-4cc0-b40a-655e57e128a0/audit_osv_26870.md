# [H] mlx5: fix skb leak while fifo resync and push

## Summary
Severity: High
Advisory: CVE-2023-54238
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-30
Source: https://osv.dev/vulnerability/CVE-2023-54238
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <6.1.18, >=6.2.0 <6.2.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

mlx5: fix skb leak while fifo resync and push

During ptp resync operation SKBs were poped from the fifo but were never
freed neither by napi_consume nor by dev_kfree_skb_any. Add call to
napi_consume_skb to properly free SKBs.

Another leak was happening because mlx5e_skb_fifo_has_room() had an error
in the check. Comparing free running counters works well unless C promotes
the types to something wider than the counter. In this case counters are
u16 but the result of the substraction is promouted to int and it causes
wrong result (negative value) of the check when producer have already
overlapped but consumer haven't yet. Explicit cast to u16 fixes the issue.

## References
- https://git.kernel.org/stable/c/234cffda95e1049f58e8ec136ef105c633f0ed19
- https://git.kernel.org/stable/c/68504c66d08c70fb92799722e25a932d311d74fd
- https://git.kernel.org/stable/c/e435941b1da1a0be4ff8a7ae425774c76a5ac514
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/54xxx/CVE-2023-54238.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-54238
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
