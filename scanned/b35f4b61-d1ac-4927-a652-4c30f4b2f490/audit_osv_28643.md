# [H] io_uring/net: fix overflow check in io_recvmsg_mshot_prep()

## Summary
Severity: High
Advisory: CVE-2024-35827
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-17
Source: https://osv.dev/vulnerability/CVE-2024-35827
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <6.1.83, >=6.2.0 <6.6.23, >=6.7.0 <6.7.11, >=6.8.0 <6.8.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

io_uring/net: fix overflow check in io_recvmsg_mshot_prep()

The "controllen" variable is type size_t (unsigned long).  Casting it
to int could lead to an integer underflow.

The check_add_overflow() function considers the type of the destination
which is type int.  If we add two positive values and the result cannot
fit in an integer then that's counted as an overflow.

However, if we cast "controllen" to an int and it turns negative, then
negative values *can* fit into an int type so there is no overflow.

Good: 100 + (unsigned long)-4 = 96  <-- overflow
 Bad: 100 + (int)-4 = 96 <-- no overflow

I deleted the cast of the sizeof() as well.  That's not a bug but the
cast is unnecessary.

## References
- https://git.kernel.org/stable/c/0c8c74bb59e7d77554016efc34c2d10376985e5e
- https://git.kernel.org/stable/c/59a534690ecc3af72c6ab121aeac1237a4adae66
- https://git.kernel.org/stable/c/868ec868616438df487b9e2baa5a99f8662cc47c
- https://git.kernel.org/stable/c/8ede3db5061bb1fe28e2c9683329aafa89d2b1b4
- https://git.kernel.org/stable/c/b6563ad0d599110bd5cf8f56c47d279c3ed796fe
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35827.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-35827
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
