# [H] RDMA/mlx5: Release the HW‑provided UAR index rather than the SW one

## Summary
Severity: High
Advisory: CVE-2026-74296
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74296
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/mlx5: Release the HW‑provided UAR index rather than the SW one

Free the UAR index returned by the hardware.

## References
- https://git.kernel.org/stable/c/449ae7927152e46acbe5f19f97eafdae6d3a96b1
- https://git.kernel.org/stable/c/6f83de384ca582fa87b4c2b0d03bd1ed3bf9a2ee
- https://git.kernel.org/stable/c/80f1f49f53a42733e60c90e0ec545e647969214d
- https://git.kernel.org/stable/c/aabfc845838ef453f1d22d7665596f9cc48be7dd
- https://git.kernel.org/stable/c/d3ff718c0c7153e2641e6a09507bace14fc5c402
- https://git.kernel.org/stable/c/ef369446f62903ea079e8a7954b5bf8bb8300fe3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74296.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74296
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
