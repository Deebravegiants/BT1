# [M] RDMA/mlx5: Fix memory leak in error flow for subscribe event routine

## Summary
Severity: Medium
Advisory: CVE-2022-49206
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49206
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.3.0 <5.4.189, >=5.5.0 <5.10.110, >=5.11.0 <5.15.33, >=5.16.0 <5.16.19, >=5.17.0 <5.17.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/mlx5: Fix memory leak in error flow for subscribe event routine

In case the second xa_insert() fails, the obj_event is not released.  Fix
the error unwind flow to free that memory to avoid a memory leak.

## References
- https://git.kernel.org/stable/c/0174a89663a5ef83617da15bf24c0af2f62b6c7f
- https://git.kernel.org/stable/c/087f9c3f2309ed183f7e4b85ae57121d8663224d
- https://git.kernel.org/stable/c/414b4e8738484379f18d6c4e780787c80dbf8a2c
- https://git.kernel.org/stable/c/8dd392e352d3269938fea32061a74655a613f929
- https://git.kernel.org/stable/c/c98d903ff9e79c210beddea4e6bc15ac38e25aa5
- https://git.kernel.org/stable/c/d66498507801fd9a20307a15a0814a0a016c3cde
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49206.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49206
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
