# [H] CVE-2014-9922

## Summary
Severity: High
Advisory: CVE-2014-9922
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-04-04
Source: https://osv.dev/vulnerability/CVE-2014-9922
Type: osv

## Details
The eCryptfs subsystem in the Linux kernel before 3.18 allows local users to gain privileges via a large filesystem stack that includes an overlayfs layer, related to fs/ecryptfs/main.c and fs/overlayfs/super.c.

## References
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=69c433ed2ecd2d3264efd7afec4439524b319121
- http://source.android.com/security/bulletin/2017-04-01.html
- http://www.securityfocus.com/bid/97354
- https://github.com/torvalds/linux/commit/69c433ed2ecd2d3264efd7afec4439524b319121
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=69c433ed2ecd2d3264efd7afec4439524b319121
- http://source.android.com/security/bulletin/2017-04-01.html
- https://github.com/torvalds/linux/commit/69c433ed2ecd2d3264efd7afec4439524b319121
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=69c433ed2ecd2d3264efd7afec4439524b319121
- https://github.com/torvalds/linux/commit/69c433ed2ecd2d3264efd7afec4439524b319121
- http://www.securitytracker.com/id/1038201
