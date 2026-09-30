# [M] drm/msm/dpu: check dpu_plane_atomic_print_state() for valid sspp

## Summary
Severity: Medium
Advisory: CVE-2024-58073
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-03-06
Source: https://osv.dev/vulnerability/CVE-2024-58073
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.13.0 <6.13.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/msm/dpu: check dpu_plane_atomic_print_state() for valid sspp

Similar to the r_pipe sspp protect, add a check to protect
the pipe state prints to avoid NULL ptr dereference for cases when
the state is dumped without a corresponding atomic_check() where the
pipe->sspp is assigned.

Patchwork: https://patchwork.freedesktop.org/patch/628404/

## References
- https://git.kernel.org/stable/c/008af2074e4b91d34440102501b710c235a3b245
- https://git.kernel.org/stable/c/789384eb1437aed94155dc0eac8a8a6ba1baf578
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/58xxx/CVE-2024-58073.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-58073
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
