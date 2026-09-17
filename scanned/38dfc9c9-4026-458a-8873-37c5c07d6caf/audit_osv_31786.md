# [M] can: rockchip: rkcanfd_handle_rx_fifo_overflow_int(): bail out if skb cannot be allocated

## Summary
Severity: Medium
Advisory: CVE-2025-21774
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-27
Source: https://osv.dev/vulnerability/CVE-2025-21774
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.12.16, >=6.13.0 <6.13.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

can: rockchip: rkcanfd_handle_rx_fifo_overflow_int(): bail out if skb cannot be allocated

Fix NULL pointer check in rkcanfd_handle_rx_fifo_overflow_int() to
bail out if skb cannot be allocated.

## References
- https://git.kernel.org/stable/c/118fb35681bd2c0d2afa22f7be0ef94bb4d06849
- https://git.kernel.org/stable/c/946750e7865df2e70045071051abf768785dd570
- https://git.kernel.org/stable/c/f7f0adfe64de08803990dc4cbecd2849c04e314a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21774.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21774
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
