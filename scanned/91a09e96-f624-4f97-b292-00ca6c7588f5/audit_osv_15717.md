# [H] CVE-2019-19044

## Summary
Severity: High
Advisory: CVE-2019-19044
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-11-18
Source: https://osv.dev/vulnerability/CVE-2019-19044
Type: osv

## Details
Two memory leaks in the v3d_submit_cl_ioctl() function in drivers/gpu/drm/v3d/v3d_gem.c in the Linux kernel before 5.3.11 allow attackers to cause a denial of service (memory consumption) by triggering kcalloc() or v3d_job_init() failures, aka CID-29cd13cfd762.

## References
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.3.11
- https://security.netapp.com/advisory/ntap-20191205-0001/
- https://usn.ubuntu.com/4225-1/
- https://github.com/torvalds/linux/commit/29cd13cfd7624726d9e6becbae9aa419ef35af7f
