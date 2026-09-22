# [C] net/mlx5e: SHAMPO, Fix invalid WQ linked list unlink

## Summary
Severity: Critical
Advisory: CVE-2024-44970
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-09-04
Source: https://osv.dev/vulnerability/CVE-2024-44970
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.16.0 <6.1.105, >=6.2.0 <6.6.46, >=6.7.0 <6.10.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/mlx5e: SHAMPO, Fix invalid WQ linked list unlink

When all the strides in a WQE have been consumed, the WQE is unlinked
from the WQ linked list (mlx5_wq_ll_pop()). For SHAMPO, it is possible
to receive CQEs with 0 consumed strides for the same WQE even after the
WQE is fully consumed and unlinked. This triggers an additional unlink
for the same wqe which corrupts the linked list.

Fix this scenario by accepting 0 sized consumed strides without
unlinking the WQE again.

## References
- https://git.kernel.org/stable/c/50d8009a0ac02c3311b23a0066511f8337bd88d9
- https://git.kernel.org/stable/c/650e24748e1e0a7ff91d5c72b72a2f2a452b5b76
- https://git.kernel.org/stable/c/7b379353e9144e1f7460ff15f39862012c9d0d78
- https://git.kernel.org/stable/c/fba8334721e266f92079632598e46e5f89082f30
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/44xxx/CVE-2024-44970.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-44970
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
