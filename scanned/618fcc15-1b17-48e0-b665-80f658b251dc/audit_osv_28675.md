# [H] SUNRPC: Fix a slow server-side memory leak with RPC-over-TCP

## Summary
Severity: High
Advisory: CVE-2024-35882
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-19
Source: https://osv.dev/vulnerability/CVE-2024-35882
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.6.0 <6.6.26, >=6.7.0 <6.8.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

SUNRPC: Fix a slow server-side memory leak with RPC-over-TCP

Jan Schunk reports that his small NFS servers suffer from memory
exhaustion after just a few days. A bisect shows that commit
e18e157bb5c8 ("SUNRPC: Send RPC message on TCP with a single
sock_sendmsg() call") is the first bad commit.

That commit assumed that sock_sendmsg() releases all the pages in
the underlying bio_vec array, but the reality is that it doesn't.
svc_xprt_release() releases the rqst's response pages, but the
record marker page fragment isn't one of those, so it is never
released.

This is a narrow fix that can be applied to stable kernels. A
more extensive fix is in the works.

## References
- https://git.kernel.org/stable/c/05258a0a69b3c5d2c003f818702c0a52b6fea861
- https://git.kernel.org/stable/c/1ba1291172f935e6b6fe703161a948f3347400b8
- https://git.kernel.org/stable/c/a2ebedf7bcd17a1194a0a18122c885eb578ee882
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35882.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-35882
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
