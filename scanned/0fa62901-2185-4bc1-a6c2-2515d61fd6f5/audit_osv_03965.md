# [H] ALPINE-CVE-2026-78410

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-78410
Ecosystem: Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-09-02
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-78410
Type: osv

## Affected
- Alpine:v3.22: `util-linux` — affected >=0 <2.41.6-r0
- Alpine:v3.23: `util-linux` — affected >=0 <2.41.6-r0
- Alpine:v3.24: `util-linux` — affected >=0 <2.42.3-r0

## Details
A flaw was found in util-linux. Restricted bind mounts take the source path from fstab but do not pin that source before the privileged mount. A local unprivileged user who can replace the authorized source or a writable ancestor can redirect SUID mount(8) to bind another host directory. If the fstab entry also sets X-mount.owner, X-mount.group, or X-mount.mode, root then changes ownership or mode on that redirected inode.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-78410
