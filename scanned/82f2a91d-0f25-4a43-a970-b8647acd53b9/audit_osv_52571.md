# [M] CVE-2021-47593

## Summary
Severity: Medium
Advisory: CVE-2021-47593
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-06-19
Source: https://osv.dev/vulnerability/CVE-2021-47593
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

mptcp: clear 'kern' flag from fallback sockets

The mptcp ULP extension relies on sk->sk_sock_kern being set correctly:
It prevents setsockopt(fd, IPPROTO_TCP, TCP_ULP, "mptcp", 6); from
working for plain tcp sockets (any userspace-exposed socket).

But in case of fallback, accept() can return a plain tcp sk.
In such case, sk is still tagged as 'kernel' and setsockopt will work.

This will crash the kernel, The subflow extension has a NULL ctx->conn
mptcp socket:

BUG: KASAN: null-ptr-deref in subflow_data_ready+0x181/0x2b0
Call Trace:
 tcp_data_ready+0xf8/0x370
 [..]

## References
- https://git.kernel.org/stable/c/451f1eded7f56e93aaf52eb547ba97742d9c0e97
- https://git.kernel.org/stable/c/c26ac0ea3a91c210cf90452e625dc441adf3e549
- https://git.kernel.org/stable/c/d6692b3b97bdc165d150f4c1505751a323a80717
