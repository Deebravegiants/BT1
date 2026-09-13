# [H] drm/vmwgfx: Fix stale file descriptors on failed usercopy

## Summary
Severity: High
Advisory: CVE-2022-48771
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-06-20
Source: https://osv.dev/vulnerability/CVE-2022-48771
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.14.0 <4.14.264, >=4.15.0 <4.19.227, >=4.20.0 <5.4.175, >=5.5.0 <5.10.95, >=5.11.0 <5.15.18, >=5.16.0 <5.16.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/vmwgfx: Fix stale file descriptors on failed usercopy

A failing usercopy of the fence_rep object will lead to a stale entry in
the file descriptor table as put_unused_fd() won't release it. This
enables userland to refer to a dangling 'file' object through that still
valid file descriptor, leading to all kinds of use-after-free
exploitation scenarios.

Fix this by deferring the call to fd_install() until after the usercopy
has succeeded.

## References
- https://git.kernel.org/stable/c/0008a0c78fc33a84e2212a7c04e6b21a36ca6f4d
- https://git.kernel.org/stable/c/1d833b27fb708d6fdf5de9f6b3a8be4bd4321565
- https://git.kernel.org/stable/c/6066977961fc6f437bc064f628cf9b0e4571c56c
- https://git.kernel.org/stable/c/84b1259fe36ae0915f3d6ddcea6377779de48b82
- https://git.kernel.org/stable/c/a0f90c8815706981c483a652a6aefca51a5e191c
- https://git.kernel.org/stable/c/ae2b20f27732fe92055d9e7b350abc5cdf3e2414
- https://git.kernel.org/stable/c/e8d092a62449dcfc73517ca43963d2b8f44d0516
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48771.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-48771
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
