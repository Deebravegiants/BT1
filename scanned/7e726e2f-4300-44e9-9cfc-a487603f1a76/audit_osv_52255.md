# [M] CVE-2021-47249

## Summary
Severity: Medium
Advisory: CVE-2021-47249
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47249
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: rds: fix memory leak in rds_recvmsg

Syzbot reported memory leak in rds. The problem
was in unputted refcount in case of error.

int rds_recvmsg(struct socket *sock, struct msghdr *msg, size_t size,
		int msg_flags)
{
...

	if (!rds_next_incoming(rs, &inc)) {
		...
	}

After this "if" inc refcount incremented and

	if (rds_cmsg_recv(inc, msg, rs)) {
		ret = -EFAULT;
		goto out;
	}
...
out:
	return ret;
}

in case of rds_cmsg_recv() fail the refcount won't be
decremented. And it's easy to see from ftrace log, that
rds_inc_addref() don't have rds_inc_put() pair in
rds_recvmsg() after rds_cmsg_recv()

 1)               |  rds_recvmsg() {
 1)   3.721 us    |    rds_inc_addref();
 1)   3.853 us    |    rds_message_inc_copy_to_user();
 1) + 10.395 us   |    rds_cmsg_recv();
 1) + 34.260 us   |  }

## References
- https://git.kernel.org/stable/c/2038cd15eacdf7512755c27686822e0052eb9042
- https://git.kernel.org/stable/c/423c6939758fb3b9cf5abbd1e7792068a5c4ae8c
- https://git.kernel.org/stable/c/49bfcbfd989a8f1f23e705759a6bb099de2cff9f
- https://git.kernel.org/stable/c/5946fbf48355f5a8caeff72580c7658da5966b86
- https://git.kernel.org/stable/c/8c3ec88b03e9e4ca117dcdc4204fd3edcd02084f
- https://git.kernel.org/stable/c/b25b60d076164edb3025e85aabd2cf50a5215b91
- https://git.kernel.org/stable/c/06b7cb0194bd1ede0dd27f3a946e7c0279fba44a
- https://git.kernel.org/stable/c/1f79bc8ae81c05eb112a53f981cb2c244ee50d02
