# [H] drm/dp_mst: Ensure mst_primary pointer is valid in drm_dp_mst_handle_up_req()

## Summary
Severity: High
Advisory: CVE-2024-57798
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-01-11
Source: https://osv.dev/vulnerability/CVE-2024-57798
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.5.0 <6.1.123, >=6.2.0 <6.6.69, >=6.7.0 <6.12.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/dp_mst: Ensure mst_primary pointer is valid in drm_dp_mst_handle_up_req()

While receiving an MST up request message from one thread in
drm_dp_mst_handle_up_req(), the MST topology could be removed from
another thread via drm_dp_mst_topology_mgr_set_mst(false), freeing
mst_primary and setting drm_dp_mst_topology_mgr::mst_primary to NULL.
This could lead to a NULL deref/use-after-free of mst_primary in
drm_dp_mst_handle_up_req().

Avoid the above by holding a reference for mst_primary in
drm_dp_mst_handle_up_req() while it's used.

v2: Fix kfreeing the request if getting an mst_primary reference fails.

## References
- https://git.kernel.org/stable/c/9735d40f5fde9970aa46e828ecc85c32571d58a2
- https://git.kernel.org/stable/c/ce55818b2d3a999f886af91679589e4644ff1dc8
- https://git.kernel.org/stable/c/e54b00086f7473dbda1a7d6fc47720ced157c6a8
- https://git.kernel.org/stable/c/f61b2e5e7821f868d6afc22382a66a30ee780ba0
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/57xxx/CVE-2024-57798.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-57798
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
