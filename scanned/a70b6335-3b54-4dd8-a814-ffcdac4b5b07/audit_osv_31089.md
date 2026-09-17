# [C] RDMA/bnxt_re: Fix max SGEs for the Work Request

## Summary
Severity: Critical
Advisory: CVE-2024-57936
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-01-21
Source: https://osv.dev/vulnerability/CVE-2024-57936
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.12.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/bnxt_re: Fix max SGEs for the Work Request

Gen P7 supports up to 13 SGEs for now. WQE software structure
can hold only 6 now. Since the max send sge is reported as
13, the stack can give requests up to 13 SGEs. This is causing
traffic failures and system crashes.

Use the define for max SGE supported for variable size. This
will work for both static and variable WQEs.

## References
- https://git.kernel.org/stable/c/3de1b50f055dc2ca7072a526cdda21f691c22dd9
- https://git.kernel.org/stable/c/79d330fbdffd8cee06d8bdf38d82cb62d8363a27
- https://git.kernel.org/stable/c/9a479088e0c8f6140b8c7752b563bc8c6c6dcc8c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/57xxx/CVE-2024-57936.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-57936
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
