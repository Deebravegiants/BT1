# [M] ip: Fix a data-race around sysctl_ip_autobind_reuse.

## Summary
Severity: Medium
Advisory: CVE-2022-49600
Ecosystem: Linux
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49600
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.7.0 <5.10.134, >=5.11.0 <5.15.58, >=5.16.0 <5.18.15

## Details
In the Linux kernel, the following vulnerability has been resolved:

ip: Fix a data-race around sysctl_ip_autobind_reuse.

While reading sysctl_ip_autobind_reuse, it can be changed concurrently.
Thus, we need to add READ_ONCE() to its reader.

## References
- https://git.kernel.org/stable/c/0db232765887d9807df8bcb7b6f29b2871539eab
- https://git.kernel.org/stable/c/611ba70e5aca252ef43374dda97ed4cf1c47a07c
- https://git.kernel.org/stable/c/87ceaa199a72c5856d49a030941fabcd5c3928d4
- https://git.kernel.org/stable/c/fa7cdcf9b28d13aac1eeb34b948db8a18e041341
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49600.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49600
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
