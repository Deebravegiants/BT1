# [H] e100: Fix possible use after free in e100_xmit_prepare

## Summary
Severity: High
Advisory: CVE-2022-49026
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2022-49026
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.3.0 <5.10.158, >=5.11.0 <5.15.82, >=5.16.0 <6.0.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

e100: Fix possible use after free in e100_xmit_prepare

In e100_xmit_prepare(), if we can't map the skb, then return -ENOMEM, so
e100_xmit_frame() will return NETDEV_TX_BUSY and the upper layer will
resend the skb. But the skb is already freed, which will cause UAF bug
when the upper layer resends the skb.

Remove the harmful free.

## References
- https://git.kernel.org/stable/c/45605c75c52c7ae7bfe902214343aabcfe5ba0ff
- https://git.kernel.org/stable/c/9fc27d22cdb9b1fcd754599d216a8992fed280cd
- https://git.kernel.org/stable/c/b46f6144ab89d3d757ead940759c505091626a7d
- https://git.kernel.org/stable/c/b775f37d943966f6f77dca402f5a9dedce502c25
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49026.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49026
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
