# [H] io_uring/cmd_net: fix wrong argument types for skb_queue_splice()

## Summary
Severity: High
Advisory: CVE-2025-68234
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-16
Source: https://osv.dev/vulnerability/CVE-2025-68234
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.17.0 <6.17.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

io_uring/cmd_net: fix wrong argument types for skb_queue_splice()

If timestamp retriving needs to be retried and the local list of
SKB's already has entries, then it's spliced back into the socket
queue. However, the arguments for the splice helper are transposed,
causing exactly the wrong direction of splicing into the on-stack
list. Fix that up.

## References
- https://git.kernel.org/stable/c/46447367a52965e9d35f112f5b26fc8ff8ec443d
- https://git.kernel.org/stable/c/c85d2cfc5e24e6866b56c7253fd4e1c7db35986c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68234.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-68234
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
