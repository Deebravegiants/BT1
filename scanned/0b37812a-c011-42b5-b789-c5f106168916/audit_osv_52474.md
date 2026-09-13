# [H] CVE-2021-47489

## Summary
Severity: High
Advisory: CVE-2021-47489
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-22
Source: https://osv.dev/vulnerability/CVE-2021-47489
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amdgpu: Fix even more out of bound writes from debugfs

CVE-2021-42327 was fixed by:

commit f23750b5b3d98653b31d4469592935ef6364ad67
Author: Thelford Williams <tdwilliamsiv@gmail.com>
Date:   Wed Oct 13 16:04:13 2021 -0400

    drm/amdgpu: fix out of bounds write

but amdgpu_dm_debugfs.c contains more of the same issue so fix the
remaining ones.

v2:
	* Add missing fix in dp_max_bpc_write (Harry Wentland)

## References
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://git.kernel.org/stable/c/1336b886b162fdc84708096ea152a61c0e1fc09c
- https://git.kernel.org/stable/c/3f4e54bd312d3dafb59daf2b97ffa08abebe60f5
- https://git.kernel.org/stable/c/9eb4bdd554fc31a5ef6bf645a20ff21618ce45a9
