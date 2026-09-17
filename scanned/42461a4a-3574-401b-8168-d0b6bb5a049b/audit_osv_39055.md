# [C] crypto: pcrypt - Fix handling of MAY_BACKLOG requests

## Summary
Severity: Critical
Advisory: CVE-2026-43493
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-19
Source: https://osv.dev/vulnerability/CVE-2026-43493
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.34 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.140, >=6.7.0 <6.12.86, >=6.13.0 <6.18.27, >=6.19.0 <7.0.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

crypto: pcrypt - Fix handling of MAY_BACKLOG requests

MAY_BACKLOG requests can return EBUSY.  Handle them by checking
for that value and filtering out EINPROGRESS notifications.

## References
- https://git.kernel.org/stable/c/1d7f07df450bac3301938fbc4251f2611be4084e
- https://git.kernel.org/stable/c/46271895ddfb1ba41f89f7e0dffbe9c2bcf7380a
- https://git.kernel.org/stable/c/76641449b28979ebd6c02e9598367e119e385236
- https://git.kernel.org/stable/c/77d55bc8675ee851ed639dc9be77325a8024cf67
- https://git.kernel.org/stable/c/915b692e6cb723aac658c25eb82c58fd81235110
- https://git.kernel.org/stable/c/9f1cbca178c03188e201ed175251372149bb25f2
- https://git.kernel.org/stable/c/ae7e95638d956d556d74b9abb9e780d3bd3dcd9e
- https://git.kernel.org/stable/c/eb34e243df57e32f4c08fa191f3602ea19076276
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43493.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43493
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
