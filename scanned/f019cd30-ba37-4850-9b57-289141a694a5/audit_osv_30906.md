# [M] drm/panel: himax-hx83102: Add a check to prevent NULL pointer dereference

## Summary
Severity: Medium
Advisory: CVE-2024-56711
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-12-29
Source: https://osv.dev/vulnerability/CVE-2024-56711
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.12.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/panel: himax-hx83102: Add a check to prevent NULL pointer dereference

drm_mode_duplicate() could return NULL due to lack of memory,
which will then call NULL pointer dereference. Add a check to
prevent it.

## References
- https://git.kernel.org/stable/c/747547972e647509815ad8530ff09d62220a56c2
- https://git.kernel.org/stable/c/e1e1af9148dc4c866eda3fb59cd6ec3c7ea34b1d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56711.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56711
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
