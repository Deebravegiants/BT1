# [H] crypto: hisilicon/qm - inject error before stopping queue

## Summary
Severity: High
Advisory: CVE-2024-47730
Ecosystem: Linux
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2024-47730
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.8.0 <5.10.235, >=5.11.0 <5.15.174, >=5.16.0 <6.1.113, >=6.2.0 <6.6.54, >=6.7.0 <6.10.13, >=6.11.0 <6.11.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

crypto: hisilicon/qm - inject error before stopping queue

The master ooo cannot be completely closed when the
accelerator core reports memory error. Therefore, the driver
needs to inject the qm error to close the master ooo. Currently,
the qm error is injected after stopping queue, memory may be
released immediately after stopping queue, causing the device to
access the released memory. Therefore, error is injected to close master
ooo before stopping queue to ensure that the device does not access
the released memory.

## References
- https://git.kernel.org/stable/c/801d64177faaec184cee1e1aa4d8487df1364a54
- https://git.kernel.org/stable/c/85e81103033324d7a271dafb584991da39554a89
- https://git.kernel.org/stable/c/98d3be34c9153eceadb56de50d9f9347e88d86e4
- https://git.kernel.org/stable/c/aa3e0db35a60002fb34ef0e4ad203aa59fd00203
- https://git.kernel.org/stable/c/b04f06fc0243600665b3b50253869533b7938468
- https://git.kernel.org/stable/c/c5f5b813e546f7fe133539c3d7a5086cc8dd2aa1
- https://git.kernel.org/stable/c/f8024f12752e32ffbbf59e1c09d949f977ff743f
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/47xxx/CVE-2024-47730.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-47730
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
