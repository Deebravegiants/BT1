# [C] libceph: refresh auth->authorizer_buf{,_len} after authorizer update

## Summary
Severity: Critical
Advisory: CVE-2026-68156
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68156
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.10.0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

libceph: refresh auth->authorizer_buf{,_len} after authorizer update

ceph_x_create_authorizer() caches au->buf->vec.iov_base and
au->buf->vec.iov_len in struct ceph_auth_handshake.  These
cached values are then used by the messenger connect code when
sending the authorizer.

ceph_x_update_authorizer() can rebuild the authorizer when a newer
service ticket is available.  If the rebuilt authorizer no longer
fits in the existing buffer, ceph_x_build_authorizer() drops its
reference to au->buf and allocates a new one.  If this is the final
reference, ceph_buffer_put() frees the old ceph_buffer and its
vec.iov_base, but auth->authorizer_buf still points at that freed
memory.

A subsequent msgr1 reconnect can therefore queue the stale pointer
and trigger a KASAN slab-use-after-free in _copy_from_iter() while
tcp_sendmsg() copies the authorizer.

Refresh auth->authorizer_buf and auth->authorizer_buf_len after a
successful authorizer rebuild so the messenger sends the current
buffer.

## References
- https://git.kernel.org/stable/c/0060ec912292a550198d8d18ac95b433c92a7091
- https://git.kernel.org/stable/c/2334e9997308305ee4fd508fdfe6086c4150ed60
- https://git.kernel.org/stable/c/26f814187abceee90dbb29a02133adb4786fbb13
- https://git.kernel.org/stable/c/5ecfcd5c05866f185357700b81b461dae4f5ebb2
- https://git.kernel.org/stable/c/75e82e8944ac1efe9fdb88bd2f14d9a031282bdf
- https://git.kernel.org/stable/c/79a273df64238a4ade8b709689a78589f755b8ef
- https://git.kernel.org/stable/c/937d61f86d377a3aa578adae7a3dfcecdddf9d89
- https://git.kernel.org/stable/c/9d37aec9ffe4e743dabc3f84502e9723e17a30d4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68156.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68156
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
