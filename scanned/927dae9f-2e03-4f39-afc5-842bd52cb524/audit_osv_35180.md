# [H] fuse: fix io-uring list corruption for terminated non-committed requests

## Summary
Severity: High
Advisory: CVE-2025-68805
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-01-13
Source: https://osv.dev/vulnerability/CVE-2025-68805
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.14.0 <6.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

fuse: fix io-uring list corruption for terminated non-committed requests

When a request is terminated before it has been committed, the request
is not removed from the queue's list. This leaves a dangling list entry
that leads to list corruption and use-after-free issues.

Remove the request from the queue's list for terminated non-committed
requests.

## References
- https://git.kernel.org/stable/c/95c39eef7c2b666026c69ab5b30471da94ea2874
- https://git.kernel.org/stable/c/a6d1f1ace16d0e777a85f84267160052d3499b6e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68805.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-68805
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
