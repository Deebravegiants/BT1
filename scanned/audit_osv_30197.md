# [M] RDMA/bnxt_re: Fix a possible memory leak

## Summary
Severity: Medium
Advisory: CVE-2024-50172
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-07
Source: https://osv.dev/vulnerability/CVE-2024-50172
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.5.0 <6.6.59, >=6.7.0 <6.11.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/bnxt_re: Fix a possible memory leak

In bnxt_re_setup_chip_ctx() when bnxt_qplib_map_db_bar() fails
driver is not freeing the memory allocated for "rdev->chip_ctx".

## References
- https://git.kernel.org/stable/c/3fc5410f225d1651580a4aeb7c72f55e28673b53
- https://git.kernel.org/stable/c/595fa9b17201028d35f92d450fc0ecda873fe469
- https://git.kernel.org/stable/c/73e04a6114e08b5eb10e589e12b680955accb376
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50172.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50172
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
