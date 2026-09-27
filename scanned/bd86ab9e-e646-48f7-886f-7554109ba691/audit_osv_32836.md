# [H] ring-buffer: Fix buffer locking in ring_buffer_subbuf_order_set()

## Summary
Severity: High
Advisory: CVE-2025-38101
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-03
Source: https://osv.dev/vulnerability/CVE-2025-38101
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.12.34, >=6.13.0 <6.15.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

ring-buffer: Fix buffer locking in ring_buffer_subbuf_order_set()

Enlarge the critical section in ring_buffer_subbuf_order_set() to
ensure that error handling takes place with per-buffer mutex held,
thus preventing list corruption and other concurrency-related issues.

## References
- https://git.kernel.org/stable/c/0fc9a295cd8e59c3636e97395e7c74a9c89fee42
- https://git.kernel.org/stable/c/40ee2afafc1d9fe3aa44a6fbe440d78a5c96a72e
- https://git.kernel.org/stable/c/e09c0600beea469b3ebf974464e526a02d59ad62
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38101.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38101
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
