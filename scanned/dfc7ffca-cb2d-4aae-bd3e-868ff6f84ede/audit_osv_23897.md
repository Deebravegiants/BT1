# [M] ipv4: Fix a data-race around sysctl_fib_sync_mem.

## Summary
Severity: Medium
Advisory: CVE-2022-49637
Ecosystem: Linux
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49637
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.2.0 <5.4.207, >=5.5.0 <5.10.132, >=5.11.0 <5.15.56, >=5.16.0 <5.18.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

ipv4: Fix a data-race around sysctl_fib_sync_mem.

While reading sysctl_fib_sync_mem, it can be changed concurrently.
So, we need to add READ_ONCE() to avoid a data-race.

## References
- https://git.kernel.org/stable/c/190cd4ff128373271e065afb20f1d2247b3f10c3
- https://git.kernel.org/stable/c/418b191d5f223a8cb6cab09eae1f72c04ba6adf2
- https://git.kernel.org/stable/c/73318c4b7dbd0e781aaababff17376b2894745c0
- https://git.kernel.org/stable/c/7c1acd98fb221dc0d847451b9ab86319f8b9916c
- https://git.kernel.org/stable/c/9be8aac91960ea32fd0e874758c9afee665c57d2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49637.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49637
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
