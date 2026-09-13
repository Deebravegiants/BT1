# [H] scsi: iscsi: iscsi_tcp: Fix null-ptr-deref while calling getpeername()

## Summary
Severity: High
Advisory: CVE-2022-50459
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-01
Source: https://osv.dev/vulnerability/CVE-2022-50459
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.9.0 <5.10.150, >=5.11.0 <5.15.75, >=5.16.0 <5.19.17, >=5.20.0 <6.0.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: iscsi: iscsi_tcp: Fix null-ptr-deref while calling getpeername()

Fix a NULL pointer crash that occurs when we are freeing the socket at the
same time we access it via sysfs.

The problem is that:

 1. iscsi_sw_tcp_conn_get_param() and iscsi_sw_tcp_host_get_param() take
    the frwd_lock and do sock_hold() then drop the frwd_lock. sock_hold()
    does a get on the "struct sock".

 2. iscsi_sw_tcp_release_conn() does sockfd_put() which does the last put
    on the "struct socket" and that does __sock_release() which sets the
    sock->ops to NULL.

 3. iscsi_sw_tcp_conn_get_param() and iscsi_sw_tcp_host_get_param() then
    call kernel_getpeername() which accesses the NULL sock->ops.

Above we do a get on the "struct sock", but we needed a get on the "struct
socket". Originally, we just held the frwd_lock the entire time but in
commit bcf3a2953d36 ("scsi: iscsi: iscsi_tcp: Avoid holding spinlock while
calling getpeername()") we switched to refcount based because the network
layer changed and started taking a mutex in that path, so we could no
longer hold the frwd_lock.

Instead of trying to maintain multiple refcounts, this just has us use a
mutex for accessing the socket in the interface code paths.

## References
- https://git.kernel.org/stable/c/0a0b861fce2657ba08ec356a74346b37ca4b2008
- https://git.kernel.org/stable/c/57569c37f0add1b6489e1a1563c71519daf732cf
- https://git.kernel.org/stable/c/884a788f065578bb640382279a83d1df433b13e6
- https://git.kernel.org/stable/c/897dbbc57d71e8a34ec1af8e573a142de457da38
- https://git.kernel.org/stable/c/a26b0658751bb0a3b28386fca715333b104d32a2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50459.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50459
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
