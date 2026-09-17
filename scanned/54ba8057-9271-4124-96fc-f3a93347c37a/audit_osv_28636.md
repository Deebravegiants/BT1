# [H] drm/vmwgfx: Fix the lifetime of the bo cursor memory

## Summary
Severity: High
Advisory: CVE-2024-35810
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-17
Source: https://osv.dev/vulnerability/CVE-2024-35810
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.2.0 <6.6.24, >=6.7.0 <6.7.12, >=6.8.0 <6.8.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/vmwgfx: Fix the lifetime of the bo cursor memory

The cleanup can be dispatched while the atomic update is still active,
which means that the memory acquired in the atomic update needs to
not be invalidated by the cleanup. The buffer objects in vmw_plane_state
instead of using the builtin map_and_cache were trying to handle
the lifetime of the mapped memory themselves, leading to crashes.

Use the map_and_cache instead of trying to manage the lifetime of the
buffer objects held by the vmw_plane_state.

Fixes kernel oops'es in IGT's kms_cursor_legacy forked-bo.

## References
- https://git.kernel.org/stable/c/104a5b2772bc7c0715ae7355ccf9d294a472765c
- https://git.kernel.org/stable/c/86cb706a40b7e6b2221ee49a298a65ad9b46c02d
- https://git.kernel.org/stable/c/9a9e8a7159ca09af9b1a300a6c8e8b6ff7501c76
- https://git.kernel.org/stable/c/ed381800ea6d9a4c7f199235a471c0c48100f0ae
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35810.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-35810
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
