# [H] io_uring/net: commit partial buffers on retry

## Summary
Severity: High
Advisory: CVE-2025-38730
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-04
Source: https://osv.dev/vulnerability/CVE-2025-38730
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.4.0 <6.6.103, >=6.7.0 <6.12.44, >=6.13.0 <6.15.11, >=6.16.0 <6.16.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

io_uring/net: commit partial buffers on retry

Ring provided buffers are potentially only valid within the single
execution context in which they were acquired. io_uring deals with this
and invalidates them on retry. But on the networking side, if
MSG_WAITALL is set, or if the socket is of the streaming type and too
little was processed, then it will hang on to the buffer rather than
recycle or commit it. This is problematic for two reasons:

1) If someone unregisters the provided buffer ring before a later retry,
   then the req->buf_list will no longer be valid.

2) If multiple sockers are using the same buffer group, then multiple
   receives can consume the same memory. This can cause data corruption
   in the application, as either receive could land in the same
   userspace buffer.

Fix this by disallowing partial retries from pinning a provided buffer
across multiple executions, if ring provided buffers are used.

## References
- https://git.kernel.org/stable/c/21a4ddb0f5e933f372808c10b9ac704505751bb1
- https://git.kernel.org/stable/c/2eb7937b5fc7fcd90eab7bebb0181214b61b9283
- https://git.kernel.org/stable/c/3b53dc1c641f2884d4750fc25aaf6c36b90db606
- https://git.kernel.org/stable/c/41b70df5b38bc80967d2e0ed55cc3c3896bba781
- https://git.kernel.org/stable/c/fe9da1812f8697a38f7e30991d568ec199e16059
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38730.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38730
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
