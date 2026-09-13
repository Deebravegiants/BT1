# [H] net: sxgbe: fix potential NULL dereference in sxgbe_rx()

## Summary
Severity: High
Advisory: CVE-2025-68302
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-12-16
Source: https://osv.dev/vulnerability/CVE-2025-68302
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.15.0 <5.10.247, >=5.11.0 <5.15.197, >=5.16.0 <6.1.159, >=6.2.0 <6.6.119, >=6.7.0 <6.12.61, >=6.13.0 <6.17.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: sxgbe: fix potential NULL dereference in sxgbe_rx()

Currently, when skb is null, the driver prints an error and then
dereferences skb on the next line.

To fix this, let's add a 'break' after the error message to switch
to sxgbe_rx_refill(), which is similar to the approach taken by the
other drivers in this particular case, e.g. calxeda with xgmac_rx().

Found during a code review.

## References
- https://git.kernel.org/stable/c/18ef3ad1bb57dcf1a9ee61736039aedccf670b21
- https://git.kernel.org/stable/c/45b5b4ddb8d6bea5fc1625ff6f163bbb125d49cc
- https://git.kernel.org/stable/c/46e5332126596a2ca791140feab18ce1fc1a3c86
- https://git.kernel.org/stable/c/7fd789d6ea4915034eb6bcb72f6883c8151083e5
- https://git.kernel.org/stable/c/88f46c0be77bfe45830ac33102c75be7c34ac3f3
- https://git.kernel.org/stable/c/ac171c3c755499c9f87fe30b920602255f8b5648
- https://git.kernel.org/stable/c/f5bce28f6b9125502abec4a67d68eabcd24b3b17
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68302.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-68302
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
