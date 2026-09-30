# [H] ipv6: ioam: fix potential NULL dereferences in __ioam6_fill_trace_data()

## Summary
Severity: High
Advisory: CVE-2026-43101
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-06
Source: https://osv.dev/vulnerability/CVE-2026-43101
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <6.18.24, >=6.19.0 <6.19.14

## Details
In the Linux kernel, the following vulnerability has been resolved:

ipv6: ioam: fix potential NULL dereferences in __ioam6_fill_trace_data()

We need to check __in6_dev_get() for possible NULL value, as
suggested by Yiming Qian.

Also add skb_dst_dev_rcu() instead of skb_dst_dev(),
and two missing READ_ONCE().

Note that @dev can't be NULL.

## References
- https://git.kernel.org/stable/c/3719c234fa94c37c955b1ecd3742ef280ec135e6
- https://git.kernel.org/stable/c/4198aab6f000b4febb18ea820fea20634dd789c7
- https://git.kernel.org/stable/c/4e65a8b8daa18d63255ec58964dd192c7fdd9f8b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43101.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43101
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
