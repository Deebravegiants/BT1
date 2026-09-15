# [M] CVE-2019-19083

## Summary
Severity: Medium
Advisory: CVE-2019-19083
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-11-18
Source: https://osv.dev/vulnerability/CVE-2019-19083
Type: osv

## Details
Memory leaks in *clock_source_create() functions under drivers/gpu/drm/amd/display/dc in the Linux kernel before 5.3.8 allow attackers to cause a denial of service (memory consumption). This affects the dce112_clock_source_create() function in drivers/gpu/drm/amd/display/dc/dce112/dce112_resource.c, the dce100_clock_source_create() function in drivers/gpu/drm/amd/display/dc/dce100/dce100_resource.c, the dcn10_clock_source_create() function in drivers/gpu/drm/amd/display/dc/dcn10/dcn10_resource.c, the dcn20_clock_source_create() function in drivers/gpu/drm/amd/display/dc/dcn20/dcn20_resource.c, the dce120_clock_source_create() function in drivers/gpu/drm/amd/display/dc/dce120/dce120_resource.c, the dce110_clock_source_create() function in drivers/gpu/drm/amd/display/dc/dce110/dce110_resource.c, and the dce80_clock_source_create() function in drivers/gpu/drm/amd/display/dc/dce80/dce80_resource.c, aka CID-055e547478a1.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-12/msg00029.html
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.3.8
- https://security.netapp.com/advisory/ntap-20191205-0001/
- https://usn.ubuntu.com/4208-1/
- https://usn.ubuntu.com/4226-1/
- https://usn.ubuntu.com/4227-1/
- https://usn.ubuntu.com/4227-2/
- https://github.com/torvalds/linux/commit/055e547478a11a6360c7ce05e2afc3e366968a12
