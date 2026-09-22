# [H] CVE-2023-26242

## Summary
Severity: High
Advisory: CVE-2023-26242
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-02-21
Source: https://osv.dev/vulnerability/CVE-2023-26242
Type: osv

## Details
afu_mmio_region_get_by_offset in drivers/fpga/dfl-afu-region.c in the Linux kernel through 6.1.12 has an integer overflow.

## References
- https://patchwork.kernel.org/project/linux-fpga/patch/20230206054326.89323-1-k1rh4.lee%40gmail.com
- https://security.netapp.com/advisory/ntap-20230406-0002/
- https://bugzilla.suse.com/show_bug.cgi?id=1208518
