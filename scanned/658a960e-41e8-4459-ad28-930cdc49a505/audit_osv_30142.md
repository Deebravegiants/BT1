# [M] md/raid10: fix null ptr dereference in raid10_size()

## Summary
Severity: Medium
Advisory: CVE-2024-50109
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-05
Source: https://osv.dev/vulnerability/CVE-2024-50109
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.9.0 <6.11.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

md/raid10: fix null ptr dereference in raid10_size()

In raid10_run() if raid10_set_queue_limits() succeed, the return value
is set to zero, and if following procedures failed raid10_run() will
return zero while mddev->private is still NULL, causing null ptr
dereference in raid10_size().

Fix the problem by only overwrite the return value if
raid10_set_queue_limits() failed.

## References
- https://git.kernel.org/stable/c/825711e00117fc686ab89ac36a9a7b252dc349c6
- https://git.kernel.org/stable/c/b3054db2fd2d35f2eb3b4b5fb1407792f465391c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50109.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50109
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
