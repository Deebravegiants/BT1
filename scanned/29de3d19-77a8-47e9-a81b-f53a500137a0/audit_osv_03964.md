# [H] ALPINE-CVE-2026-78409

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-78409
Ecosystem: Alpine:v3.24
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-09-02
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-78409
Type: osv

## Affected
- Alpine:v3.24: `util-linux` — affected >=0 <2.42.3-r0

## Details
The X-mount.subdir option uses a detached-tree fast path on Linux 6.15 and later and passes the configured subdirectory to open_tree() with AT_SYMLINK_NOFOLLOW. That flag does not stop intermediate symlink traversal or keep resolution inside the newly mounted filesystem. A local unprivileged user with an fstab-authorized X-mount.subdir entry can attach a host path at the intended mountpoint.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-78409
