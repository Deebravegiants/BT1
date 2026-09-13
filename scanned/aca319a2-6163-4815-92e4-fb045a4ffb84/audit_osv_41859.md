# [H] net/iucv: fix locking in .getsockopt

## Summary
Severity: High
Advisory: CVE-2026-64004
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64004
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.4.0 <5.10.259, >=5.11.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.93, >=6.13.0 <6.18.35, >=6.19.0 <7.0.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/iucv: fix locking in .getsockopt

Mirror iucv_sock_setsockopt() and wrap the whole switch in
lock_sock()/release_sock(). The pre-existing SO_MSGLIMIT-only lock
becomes redundant and is removed.

Any AF_IUCV HIPER user can potentially crash the kernel by racing
recvmsg() with getsockopt(SO_MSGSIZE): the SO_MSGSIZE arm dereferences
iucv->hs_dev->mtu after iucv_sock_close() (called from the racing
recvmsg()) has set hs_dev to NULL, producing a NULL pointer dereference
oops.

## References
- https://git.kernel.org/stable/c/1fc30bd4e55e2dd622d2d366cecd732c1841bbee
- https://git.kernel.org/stable/c/3589d20a666caf30ad100c960a2de7de390fce88
- https://git.kernel.org/stable/c/45bb8de8c95d8899f4b8f61bd9bceb8132af73cb
- https://git.kernel.org/stable/c/69554adc7a6fa04ede3ad7512321d83748e3c920
- https://git.kernel.org/stable/c/6e792b8dd3002bbc4136745928a9605df1a72b8a
- https://git.kernel.org/stable/c/884eb247b74d86db97e3a37f0d6fc8e1e83590dd
- https://git.kernel.org/stable/c/9817369243380e287ebe5525411557eaa3aa2a79
- https://git.kernel.org/stable/c/cd691beafea0dd779e69e81ccc26b0ab50efcb5e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64004.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64004
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
