# [H] io_uring/zcrx: fix overshooting recv limit

## Summary
Severity: High
Advisory: CVE-2025-40046
Ecosystem: Linux
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:H)
Published: 2025-10-28
Source: https://osv.dev/vulnerability/CVE-2025-40046
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.15.0 <6.17.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

io_uring/zcrx: fix overshooting recv limit

It's reported that sometimes a zcrx request can receive more than was
requested. It's caused by io_zcrx_recv_skb() adjusting desc->count for
all received buffers including frag lists, but then doing recursive
calls to process frag list skbs, which leads to desc->count double
accounting and underflow.

## References
- https://git.kernel.org/stable/c/09cfd3c52ea76f43b3cb15e570aeddf633d65e80
- https://git.kernel.org/stable/c/8bcc9eaf1b19f1a7029cba19f6bd4122b40f6c4f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40046.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40046
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
