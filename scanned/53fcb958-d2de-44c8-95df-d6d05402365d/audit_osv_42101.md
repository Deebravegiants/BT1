# [C] net/handshake: Take a long-lived file reference at submit

## Summary
Severity: Critical
Advisory: CVE-2026-64523
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64523
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.4.0 <6.12.93, >=6.13.0 <6.18.44, >=6.19.0 <7.0.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/handshake: Take a long-lived file reference at submit

handshake_nl_accept_doit() needs the file pointer backing
req->hr_sk->sk_socket to survive the window between
handshake_req_next() and the subsequent FD_PREPARE() and get_file().
The submit-side sock_hold() does not provide that.  sk_refcnt keeps
struct sock alive, but struct socket is owned by sock->file: when
the consumer fputs the last file reference, sock_release() tears
the socket down regardless of any sock_hold.

Add an hr_file pointer to struct handshake_req and acquire an
explicit reference on sock->file during handshake_req_submit().
handshake_complete() and handshake_req_cancel() release the
reference on the completion-bit-winning path.

The submit error path must also release the file reference, but
after rhashtable insertion a concurrent handshake_req_cancel() can
discover the request and race the error path.  Gate the error-path
cleanup -- sk_destruct restoration, fput, and request destruction
-- with test_and_set_bit(HANDSHAKE_F_REQ_COMPLETED), the same
serialization handshake_complete() and handshake_req_cancel()
already use.  When cancel has already claimed ownership, the submit
error path returns without touching the request; socket teardown
handles final destruction.

The accept-side dereferences are not yet retargeted; that change
comes in the next patch.

## References
- https://git.kernel.org/stable/c/09dba37eee70d0596e26645015f1aa95a9848e9d
- https://git.kernel.org/stable/c/16eaba5aa89c04eea125905bb8f988c1897f4f29
- https://git.kernel.org/stable/c/685b10dd0e32c7782cead16c8cf055c609678583
- https://git.kernel.org/stable/c/b913801ad9b9a51437d84d030ec6843e08976bd6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64523.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64523
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
