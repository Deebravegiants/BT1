# [M] RDMA/uverbs: Prevent integer overflow issue

## Summary
Severity: Medium
Advisory: CVE-2024-57890
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-01-15
Source: https://osv.dev/vulnerability/CVE-2024-57890
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.15 <5.4.289, >=5.5.0 <5.10.233, >=5.11.0 <5.15.176, >=5.16.0 <6.1.124, >=6.2.0 <6.6.70, >=6.7.0 <6.12.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/uverbs: Prevent integer overflow issue

In the expression "cmd.wqe_size * cmd.wr_count", both variables are u32
values that come from the user so the multiplication can lead to integer
wrapping.  Then we pass the result to uverbs_request_next_ptr() which also
could potentially wrap.  The "cmd.sge_count * sizeof(struct ib_uverbs_sge)"
multiplication can also overflow on 32bit systems although it's fine on
64bit systems.

This patch does two things.  First, I've re-arranged the condition in
uverbs_request_next_ptr() so that the use controlled variable "len" is on
one side of the comparison by itself without any math.  Then I've modified
all the callers to use size_mul() for the multiplications.

## References
- https://git.kernel.org/stable/c/346db03e9926ab7117ed9bf19665699c037c773c
- https://git.kernel.org/stable/c/42a6eb4ed7a9a41ba0b83eb0c7e0225b5fca5608
- https://git.kernel.org/stable/c/b3ef4ae713360501182695dd47d6b4f6e1a43eb8
- https://git.kernel.org/stable/c/b92667f755749cf10d9ef1088865c555ae83ffb7
- https://git.kernel.org/stable/c/c2f961c46ea0e5274c5c320d007c2dd949cf627a
- https://git.kernel.org/stable/c/c57721b24bd897338a81a0ca5fff41600f0f1ad1
- https://git.kernel.org/stable/c/d0257e089d1bbd35c69b6c97ff73e3690ab149a9
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/57xxx/CVE-2024-57890.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-57890
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
