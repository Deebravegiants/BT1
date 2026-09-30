# [M] CVE-2022-3061

## Summary
Severity: Medium
Advisory: CVE-2022-3061
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-09-01
Source: https://osv.dev/vulnerability/CVE-2022-3061
Type: osv

## Details
Found Linux Kernel flaw in the i740 driver. The Userspace program could pass any values to the driver through ioctl() interface. The driver doesn't check the value of 'pixclock', so it may cause a divide by zero error.

## References
- https://lists.debian.org/debian-lts-announce/2022/11/msg00001.html
- https://www.debian.org/security/2022/dsa-5257
- https://git.kernel.org/pub/scm/linux/kernel/git/deller/linux-fbdev.git/commit/?id=15cf0b82271b1823fb02ab8c377badba614d95d5
