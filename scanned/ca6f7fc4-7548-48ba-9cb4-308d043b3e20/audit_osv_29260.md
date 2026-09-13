# [H] nvmet: always initialize cqe.result

## Summary
Severity: High
Advisory: CVE-2024-41079
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-07-29
Source: https://osv.dev/vulnerability/CVE-2024-41079
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.8.0 <5.15.209, >=5.16.0 <6.1.101, >=6.2.0 <6.6.42, >=6.7.0 <6.9.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

nvmet: always initialize cqe.result

The spec doesn't mandate that the first two double words (aka results)
for the command queue entry need to be set to 0 when they are not
used (not specified). Though, the target implemention returns 0 for TCP
and FC but not for RDMA.

Let's make RDMA behave the same and thus explicitly initializing the
result field. This prevents leaking any data from the stack.

## References
- https://git.kernel.org/stable/c/0990e8a863645496b9e3f91cfcfd63cd95c80319
- https://git.kernel.org/stable/c/10967873b80742261527a071954be8b54f0f8e4d
- https://git.kernel.org/stable/c/30d35b24b7957922f81cfdaa66f2e1b1e9b9aed2
- https://git.kernel.org/stable/c/c6a2cf8b0764f3ba7d9bff58c8775a6d4476bb29
- https://git.kernel.org/stable/c/cd0c1b8e045a8d2785342b385cb2684d9b48e426
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/41xxx/CVE-2024-41079.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-41079
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
