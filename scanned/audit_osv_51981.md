# [M] CVE-2021-46923

## Summary
Severity: Medium
Advisory: CVE-2021-46923
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-02-27
Source: https://osv.dev/vulnerability/CVE-2021-46923
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

fs/mount_setattr: always cleanup mount_kattr

Make sure that finish_mount_kattr() is called after mount_kattr was
succesfully built in both the success and failure case to prevent
leaking any references we took when we built it.  We returned early if
path lookup failed thereby risking to leak an additional reference we
took when building mount_kattr when an idmapped mount was requested.

## References
- https://git.kernel.org/stable/c/012e332286e2bb9f6ac77d195f17e74b2963d663
- https://git.kernel.org/stable/c/47b5d0a7532d39e42a938f81e3904268145c341d
