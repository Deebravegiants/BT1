# [M] RDMA/hns: Fix cpu stuck caused by printings during reset

## Summary
Severity: Medium
Advisory: CVE-2024-56722
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-12-29
Source: https://osv.dev/vulnerability/CVE-2024-56722
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.9.0 <6.1.120, >=6.2.0 <6.6.64, >=6.7.0 <6.11.11, >=6.12.0 <6.12.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/hns: Fix cpu stuck caused by printings during reset

During reset, cmd to destroy resources such as qp, cq, and mr may fail,
and error logs will be printed. When a large number of resources are
destroyed, there will be lots of printings, and it may lead to a cpu
stuck.

Delete some unnecessary printings and replace other printing functions
in these paths with the ratelimited version.

## References
- https://git.kernel.org/stable/c/31c6fe9b79ed42440094f2367897aea0c0ce96ec
- https://git.kernel.org/stable/c/323275ac2ff15b2b7b3eac391ae5d8c5a3c3a999
- https://git.kernel.org/stable/c/a0e4c78770faa0d56d47391476fe1d827e72eded
- https://git.kernel.org/stable/c/b4ba31e5aaffbda9b22d9a35c40b16dc39e475a6
- https://git.kernel.org/stable/c/e2e64f9c42c717beb459ab209ec1c4baa73d3760
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56722.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56722
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
