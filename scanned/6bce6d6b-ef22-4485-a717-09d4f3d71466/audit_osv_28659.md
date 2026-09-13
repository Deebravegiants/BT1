# [M] block: fix module reference leakage from bdev_open_by_dev error path

## Summary
Severity: Medium
Advisory: CVE-2024-35859
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-17
Source: https://osv.dev/vulnerability/CVE-2024-35859
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.8.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

block: fix module reference leakage from bdev_open_by_dev error path

At the time bdev_may_open() is called, module reference is grabbed
already, hence module reference should be released if bdev_may_open()
failed.

This problem is found by code review.

## References
- https://git.kernel.org/stable/c/0e9327c67410b129bf85e5c3a5aaea518328636f
- https://git.kernel.org/stable/c/9617cd6f24b294552a817f80f5225431ef67b540
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35859.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-35859
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
