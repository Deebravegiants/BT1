# [H] tcp: Correct signedness in skb remaining space calculation

## Summary
Severity: High
Advisory: CVE-2025-38463
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-25
Source: https://osv.dev/vulnerability/CVE-2025-38463
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.5.0 <6.6.99, >=6.7.0 <6.12.39, >=6.13.0 <6.15.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

tcp: Correct signedness in skb remaining space calculation

Syzkaller reported a bug [1] where sk->sk_forward_alloc can overflow.

When we send data, if an skb exists at the tail of the write queue, the
kernel will attempt to append the new data to that skb. However, the code
that checks for available space in the skb is flawed:
'''
copy = size_goal - skb->len
'''

The types of the variables involved are:
'''
copy: ssize_t (s64 on 64-bit systems)
size_goal: int
skb->len: unsigned int
'''

Due to C's type promotion rules, the signed size_goal is converted to an
unsigned int to match skb->len before the subtraction. The result is an
unsigned int.

When this unsigned int result is then assigned to the s64 copy variable,
it is zero-extended, preserving its non-negative value. Consequently, copy
is always >= 0.

Assume we are sending 2GB of data and size_goal has been adjusted to a
value smaller than skb->len. The subtraction will result in copy holding a
very large positive integer. In the subsequent logic, this large value is
used to update sk->sk_forward_alloc, which can easily cause it to overflow.

The syzkaller reproducer uses TCP_REPAIR to reliably create this
condition. However, this can also occur in real-world scenarios. The
tcp_bound_to_half_wnd() function can also reduce size_goal to a small
value. This would cause the subsequent tcp_wmem_schedule() to set
sk->sk_forward_alloc to a value close to INT_MAX. Further memory
allocation requests would then cause sk_forward_alloc to wrap around and
become negative.

[1]: https://syzkaller.appspot.com/bug?extid=de6565462ab540f50e47

## References
- https://git.kernel.org/stable/c/62e6160cfb5514787bda833d466509edc38fde23
- https://git.kernel.org/stable/c/81373cd1d72d87c7d844d4454a526b8f53e72d00
- https://git.kernel.org/stable/c/9f164fa6bb09fbcc60fa5c3ff551ce9eec1befd7
- https://git.kernel.org/stable/c/d3a5f2871adc0c61c61869f37f3e697d97f03d8c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38463.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38463
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
