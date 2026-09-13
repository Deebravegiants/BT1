# [H] io_uring/rw: split io_read() into a helper

## Summary
Severity: High
Advisory: CVE-2023-52926
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-24
Source: https://osv.dev/vulnerability/CVE-2023-52926
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.1.0 <6.1.122, >=6.2.0 <6.6.68

## Details
In the Linux kernel, the following vulnerability has been resolved:

IORING_OP_READ did not correctly consume the provided buffer list when
read i/o returned < 0 (except for -EAGAIN and -EIOCBQUEUED return).
This can lead to a potential use-after-free when the completion via
io_rw_done runs at separate context.

## References
- https://git.kernel.org/stable/c/6c27fc6a783c8a77c756dd5461b15e465020d075
- https://git.kernel.org/stable/c/72060434a14caea20925e492310d6e680e3f9007
- https://git.kernel.org/stable/c/a08d195b586a217d76b42062f88f375a3eedda4d
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52926.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52926
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
